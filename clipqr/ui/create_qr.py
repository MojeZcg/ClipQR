"""Ventana «Crear QR»: formulario por tipo, vista previa en vivo y exportación (copiar, PNG, SVG)."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import ImageTk

from clipqr import APP_NAME
from clipqr import generate as g
from clipqr.actions import current_wifi
from clipqr.i18n import N_, _
from clipqr.icons import make_icon
from clipqr.settings import save_state
from clipqr.ui.theme import KINDS, THEMES
from clipqr.platform import clipboard_token, copy_image_to_clipboard, style_window
from clipqr.ui.system_texts import read_wifi_question

TYPES = (("text", N_("Texto o enlace")), ("wifi", "Wi‑Fi"), ("contact", N_("Contacto")), ("email", "Email"),
         ("phone", N_("Teléfono")), ("sms", "SMS"), ("whatsapp", "WhatsApp"), ("geo", N_("Ubicación")))
# tipo -> [(clave, etiqueta, multilínea)]
FIELDS = {
    "text": [("text", N_("Texto o enlace"), True)],
    "wifi": [("ssid", N_("Nombre de la red"), False), ("password", N_("Contraseña"), False)],
    "contact": [("name", N_("Nombre"), False), ("phone", N_("Teléfono"), False), ("email", "Email", False),
                ("org", N_("Empresa"), False), ("url", N_("Web"), False)],
    "email": [("to", N_("Para"), False), ("subject", N_("Asunto"), False), ("body", N_("Mensaje"), True)],
    "phone": [("number", N_("Número"), False)],
    "sms": [("number", N_("Número"), False), ("message", N_("Mensaje"), True)],
    "whatsapp": [("number", N_("Número con prefijo de país"), False), ("message", N_("Mensaje (opcional)"), True)],
    "geo": [("lat", N_("Latitud"), False), ("lon", N_("Longitud"), False)],
}
COLORS = ((N_("Negro"), "#000000"), (N_("Azul"), "#1e3a8a"), (N_("Verde"), "#14532d"), (N_("Morado"), "#4c1d95"))


def build_payload(kind, f, wifi_security="WPA", wifi_hidden=False):
    """Contenido del QR a partir de los campos del formulario (o "" si falta lo imprescindible)."""
    if kind == "text":
        return g.build_url(f["text"]) if f["text"].strip() else ""
    if kind == "wifi":
        return g.build_wifi(f["ssid"], f["password"], wifi_security, wifi_hidden) if f["ssid"] else ""
    if kind == "contact":
        return g.build_vcard(f["name"], f["phone"], f["email"], f["org"], f["url"]) if any(f.values()) else ""
    if kind == "email":
        return g.build_email(f["to"], f["subject"], f["body"]) if f["to"] else ""
    if kind == "phone":
        return g.build_tel(f["number"]) if f["number"] else ""
    if kind == "sms":
        return g.build_sms(f["number"], f["message"]) if f["number"] else ""
    if kind == "whatsapp":
        return g.build_whatsapp(f["number"], f["message"]) if f["number"] else ""
    if kind == "geo":
        try:
            return g.build_geo(f["lat"].replace(",", "."), f["lon"].replace(",", "."))
        except ValueError:
            return ""
    return ""


class CreateQRMixin:
    def show_create_qr(self, text=None):
        if getattr(self, "create_win", None) is not None and self.create_win.winfo_exists():
            self.create_win.deiconify()
            self.create_win.lift()
            self.create_win.focus_force()
            return
        if text is None:  # lo que haya copiado (si es texto) sirve de punto de partida
            try:
                text = self.root.clipboard_get()
            except tk.TclError:
                text = ""
            text = text if len(text) <= 2000 else ""
        self.c = THEMES[self.theme_name()]
        c = self.c
        win = tk.Toplevel(self.root, bg=c["bg"])
        self.create_win = win
        win.title(f"{APP_NAME} · {_('Crear QR')}")
        win.minsize(self.px(760), self.px(560))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")
        self._window_header(win, _("Crear QR"), _("Elige el tipo, rellena los datos y copia o guarda el código"))

        st = {"kind": "text", "security": "WPA", "hidden": False, "ec": "M", "logo": False,
              "fg": "#000000", "img": None, "payload": "", "job": None}
        vars_ = {}
        body = tk.Frame(win, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=self.px(16), pady=(self.px(4), self.px(16)))
        left = tk.Frame(body, bg=c["bg"])
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
        right.pack(side="right", fill="y", padx=(self.px(16), 0))

        def label(parent, text):
            tk.Label(parent, text=text, bg=parent.cget("bg"), fg=c["muted"], font=self.font(9, "bold"),
                     anchor="w").pack(fill="x", pady=(self.px(10), self.px(4)))

        # tipo: dos filas de botones
        label(left, _("TIPO"))
        rows = [tk.Frame(left, bg=c["bg"]) for __ in range(2)]
        for r in rows:
            r.pack(fill="x")
        type_buttons = {}

        def paint_types():
            for key, b in type_buttons.items():
                sel = key == st["kind"]
                b._base_bg = KINDS["link"][2] if sel else c["btn"]
                b._base_fg = "white" if sel else c["fg"]
                b.config(bg=b._base_bg, fg=b._base_fg)

        for i, (key, name) in enumerate(TYPES):
            b = self._button(rows[i // 4], _(name), cmd=lambda k=key: set_kind(k))
            b.pack(side="left", padx=(0, self.px(4)), pady=self.px(2))
            type_buttons[key] = b

        label(left, _("DATOS"))
        form = tk.Frame(left, bg=c["bg"])
        form.pack(fill="x")

        def field(parent, key, title, multiline, value=""):
            tk.Label(parent, text=_(title), bg=c["bg"], fg=c["fg"], font=self.font(9), anchor="w").pack(fill="x")
            box = tk.Frame(parent, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
            box.pack(fill="x", pady=(self.px(2), self.px(8)))
            if multiline:
                w = tk.Text(box, height=4, wrap="word", bg=c["card"], fg=c["fg"], insertbackground=c["fg"],
                            relief="flat", font=self.font(10), highlightthickness=0, padx=self.px(6), pady=self.px(4))
                w.insert("1.0", value)
                w.bind("<<Modified>>", lambda e: (w.edit_modified(False), schedule()))
                vars_[key] = lambda w=w: w.get("1.0", "end-1c")
            else:
                var = tk.StringVar(value=value)
                var.trace_add("write", lambda *a: schedule())
                w = tk.Entry(box, textvariable=var, bg=c["card"], fg=c["fg"], insertbackground=c["fg"], relief="flat",
                             font=self.font(10), highlightthickness=0)
                vars_[key] = var.get
                vars_["_set_" + key] = var.set
            w.pack(fill="x", padx=self.px(6), pady=self.px(4))
            return w

        def build_form():
            for w in form.winfo_children():
                w.destroy()
            vars_.clear()
            first = None
            for key, title, multi in FIELDS[st["kind"]]:
                w = field(form, key, title, multi, text if (st["kind"] == "text" and key == "text") else "")
                first = first or w
            if st["kind"] == "wifi":
                extra = tk.Frame(form, bg=c["bg"])
                extra.pack(fill="x")
                self._segmented(extra, [("WPA", "WPA/WPA2/WPA3", True), ("WEP", "WEP", True)], st["security"],
                                lambda v: (st.update(security=v), schedule())).pack(side="left")
                tk.Label(extra, text="  " + _("Red oculta"), bg=c["bg"], fg=c["fg"], font=self.font(9)).pack(side="left")
                self._switch(extra, st["hidden"], lambda v: (st.update(hidden=v), schedule())).pack(side="left",
                                                                                                    padx=self.px(6))
                self._button(form, _("Usar mi Wi‑Fi actual"), cmd=fill_current_wifi).pack(anchor="w", pady=(self.px(8), 0))
            if first is not None:
                first.focus_set()

        def fill_current_wifi():
            if not messagebox.askyesno(_("Usar mi Wi‑Fi actual"), read_wifi_question(), parent=win):
                return

            def work():
                info = current_wifi()
                self.root.after(0, lambda: apply_wifi(info))

            threading.Thread(target=work, daemon=True).start()

        def apply_wifi(info):
            if not info:
                status.config(text=_("No estás conectado a ninguna Wi‑Fi."), fg=c["bad_fg"])
                return
            ssid, password, security = info
            vars_["_set_ssid"](ssid)
            vars_["_set_password"](password)
            st["security"] = security if security != "nopass" else "WPA"

        def set_kind(k):
            st["kind"] = k
            paint_types()
            build_form()
            schedule()

        # opciones
        label(left, _("OPCIONES"))
        opts = tk.Frame(left, bg=c["bg"])
        opts.pack(fill="x")
        tk.Label(opts, text=_("Corrección de errores"), bg=c["bg"], fg=c["fg"], font=self.font(9)).pack(anchor="w")
        self._segmented(opts, [(e, f"{e} ({p})", True) for e, p in zip(g.EC_LEVELS, ("7 %", "15 %", "25 %", "30 %"))],
                        st["ec"], lambda v: (st.update(ec=v), schedule())).pack(anchor="w", pady=(self.px(2), self.px(8)))
        tk.Label(opts, text="Color", bg=c["bg"], fg=c["fg"], font=self.font(9)).pack(anchor="w")
        self._segmented(opts, [(hexc, _(name), True) for name, hexc in COLORS], st["fg"],
                        lambda v: (st.update(fg=v), schedule())).pack(anchor="w", pady=(self.px(2), self.px(8)))
        logo_row = tk.Frame(opts, bg=c["bg"])
        logo_row.pack(anchor="w")
        self._switch(logo_row, st["logo"], lambda v: (st.update(logo=v), schedule())).pack(side="left")
        tk.Label(logo_row, text="  " + _("Logo de ClipQR en el centro (usa corrección H)"), bg=c["bg"], fg=c["fg"],
                 font=self.font(9)).pack(side="left")

        # vista previa y exportación
        preview = tk.Label(right, bg=c["card"], bd=0, width=self.px(300), height=self.px(300))
        preview.pack(padx=self.px(16), pady=(self.px(16), self.px(8)))
        status = tk.Label(right, bg=c["card"], fg=c["muted"], font=self.font(9), wraplength=self.px(300), justify="center")
        status.pack(padx=self.px(16))
        buttons = tk.Frame(right, bg=c["card"])
        buttons.pack(fill="x", padx=self.px(16), pady=self.px(12))
        b_copy = self._button(buttons, _("Copiar imagen"), color=KINDS["link"][2])
        b_copy.pack(fill="x", pady=(0, self.px(6)))
        b_png = self._button(buttons, _("Guardar PNG…"))
        b_png.pack(fill="x", pady=(0, self.px(6)))
        b_svg = self._button(buttons, _("Guardar SVG…"))
        b_svg.pack(fill="x")

        def schedule():
            if st["job"]:
                win.after_cancel(st["job"])
            st["job"] = win.after(150, render)

        def render():
            st["job"] = None
            fields = {k: fn() for k, fn in vars_.items() if not k.startswith("_")}
            payload = build_payload(st["kind"], fields, st["security"], st["hidden"])
            st["payload"] = payload
            ready = bool(payload)
            for b in (b_copy, b_png, b_svg):
                b.config(state="normal" if ready else "disabled")
            if not payload:
                preview.config(image="")
                status.config(text=_("Rellena los datos para ver el código."), fg=c["muted"])
                st["img"] = None
                return
            logo = make_icon(size=256) if st["logo"] else None
            try:
                img = g.make_qr(payload, ec_level=st["ec"], module=10, fg=st["fg"], logo=logo)
            except Exception:
                status.config(text=_("Demasiado texto para un código QR."), fg=c["bad_fg"])
                st["img"] = None
                return
            st["img"] = img
            photo = ImageTk.PhotoImage(img.resize((self.px(300), self.px(300))))
            self._photos.append(photo)
            preview.config(image=photo)
            if g.verify(img, payload):
                note = _("✓ Se lee correctamente")
                if g.contrast_ratio(st["fg"], "#ffffff") < 4:
                    note += " " + _("(contraste justo: puede costar con algunas cámaras)")
                status.config(text=note, fg=c["ok"] if c["ok"] else c["fg"])
            else:
                status.config(text=_("✕ No se puede leer: prueba sin logo o con más corrección."), fg=c["bad_fg"])

        def copy_image():
            if st["img"] is None:
                return
            ok = copy_image_to_clipboard(g.make_qr(st["payload"], ec_level=st["ec"], module=10, fg=st["fg"],
                                                   logo=make_icon(size=256) if st["logo"] else None))
            # no volver a escanear nuestro propio QR al copiarlo
            self.last_seq = clipboard_token()
            save_state(clip_seq=self.last_seq)
            self._flash(b_copy, _("✓ Copiada") if ok else _("No se pudo copiar"), ok=ok)

        def save_png():
            if st["img"] is None:
                return
            path = filedialog.asksaveasfilename(parent=win, defaultextension=".png", initialfile="qr.png",
                                                filetypes=[(_("Imagen PNG"), "*.png")])
            if path:
                g.make_qr(st["payload"], ec_level=st["ec"], module=20, fg=st["fg"],
                          logo=make_icon(size=512) if st["logo"] else None).save(path)
                self._flash(b_png, _("✓ Guardado"))

        def save_svg():
            if st["img"] is None:
                return
            if st["logo"]:
                messagebox.showinfo(_("Guardar SVG"), _("El SVG se guarda sin el logo (solo el código)."), parent=win)
            path = filedialog.asksaveasfilename(parent=win, defaultextension=".svg", initialfile="qr.svg",
                                                filetypes=[(_("Imagen SVG"), "*.svg")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(g.make_svg(st["payload"], ec_level=st["ec"]))
                self._flash(b_svg, _("✓ Guardado"))

        b_copy.config(command=copy_image)
        b_png.config(command=save_png)
        b_svg.config(command=save_svg)
        win.bind("<Escape>", lambda e: win.destroy())
        paint_types()
        build_form()
        render()
