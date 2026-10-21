<p align="center"><a href="PRIVACY.md">Español</a> · <b>English</b></p>

# ClipQR privacy policy

*Last updated: October 21, 2026*

ClipQR is a Windows app that detects QR codes and barcodes in the images you copy or capture. This policy explains what data it uses and what it does with it.

## Summary

**ClipQR does not collect, transmit or sell any data.** Everything is processed on your computer.

## What data the app uses

- **Clipboard images.** When you copy an image or take a screenshot, ClipQR analyzes it on your computer to look for codes. The image is not saved to disk or sent anywhere.
- **Content of detected codes.** It is shown on screen and kept in a history **in memory only**, which is cleared when you close ClipQR or press *Clear history*.
- **Settings.** Your preferences (display time, position, theme…) are stored in a local file (`settings.json`) in the app's data folder.
- **Error log.** If something goes wrong, the technical details are saved to a local file (`error.log`) so the problem can be diagnosed. It contains no images and is never sent.

## Internet connections

ClipQR only connects to the internet on its own for one thing, and it can be turned off:

- **Check for updates** (on by default; turn it off in *Settings › General*). Once a day it checks the list of published versions on GitHub (`api.github.com/repos/MojeZcg/ClipQR/releases/latest`). It sends no data about you or your codes: it's an ordinary request, and GitHub sees what any website sees (your IP address and the ClipQR version in the user agent). If there's a new version, ClipQR lets you know, and it only downloads and installs it if you press **Install**. The Microsoft Store version doesn't make this check: the Store keeps it up to date.

Beyond that, the network is used when **you** press a button that needs it, for example:

- **Open link**, **View on map**, **Search product** or **Search on Google**: your browser opens that address.
- **Write email**, **Call** or **Send SMS**: the app you have set up in Windows for that opens.
- **Connect to network**: a Wi‑Fi profile is created in Windows with the network name and password from the code, and Windows connects to that network.

What happens from there depends on those apps and websites, which have their own privacy policies.

## Third-party data

ClipQR includes no advertising, analytics, telemetry or third-party services.

## Children

ClipQR doesn't collect data from anyone, including children.

## Changes

If this policy changes, the new version will be published on this same page with its update date.

## Contact

For any privacy questions, open an issue at https://github.com/MojeZcg/ClipQR/issues.
