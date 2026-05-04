# LibreFix

**One-click fix for FreeStyle Libre Bluetooth on Fairphone after the Android 15 update.**

After the March/April 2026 Android 15 update on Fairphone 4 and 5, FreeStyle LibreLink loses its Bluetooth connection to Libre sensors. NFC manual scanning still works but continuous glucose monitoring stops. The app shows "Ready to scan" instead of live readings.

LibreFix fixes this in about 30 seconds. No technical knowledge required.

---

## Download

👉 **[Download LibreFix.exe](../../releases/latest)** from the Releases page.

No installation required. ADB is bundled inside the .exe.

---

## How to use

**On your phone first:**
1. Settings → About Phone → tap **Build Number** 7 times
2. Settings → System → Developer Options → turn on **USB Debugging**

**Then:**
1. Run **LibreFix.exe** on your Windows PC
2. Connect your phone via USB
3. Tap **Allow** when your phone asks about USB Debugging
4. Click **Fix My Libre**
5. Wait ~30 seconds
6. Open LibreLink and wait 2-3 minutes

That's it.

---

## Does it work?

Yes - tested on Fairphone 5 running FP5.VT2Q (April 2026 update) with FreeStyle Libre 2. Working for 5+ hours after applying the fix.

If it doesn't work first time, try toggling Bluetooth off and on, then run LibreFix again.

---

## Does it need root?

No. LibreFix uses ADB (Android Debug Bridge) which only requires USB Debugging to be enabled. No rooting required.

---

## What does it actually do?

LibreFix applies a set of ADB commands that restore the Bluetooth permissions and background execution rights that Android 15 has incorrectly restricted:

- Enables BLE always-on scanning
- Grants LibreLink the Bluetooth permissions Android 15 restricted
- Prevents Android killing the Bluetooth system service in the background
- Prevents Android killing LibreLink in the background  
- Whitelists LibreLink from battery optimisation
- Removes background network restrictions
- Restarts LibreLink cleanly

No data is collected. No changes are made to your phone other than the permission grants listed above. Full source code is in this repository.

---

## Important

⚠️ **Do not accept Fairphone OTA updates** until Fairphone officially fixes the Bluetooth bug. An update may undo this fix.

⚠️ If you replace your sensor, you may need to run LibreFix again.

---

## Supported devices

- Fairphone 4 (Android 15)
- Fairphone 5 (Android 15)

May work on other Android devices with the same Bluetooth issue.

## Supported LibreLink regions

Automatically detects your regional version:
UK, France, Germany, USA, Netherlands, Belgium, Spain, Italy, Sweden, Norway, Denmark, Finland, Australia, Canada.

If your region isn't listed, open an issue - we just need your package name.

---

## Background

The March/April 2026 Android 15 update on Fairphone broke BLE L2CAP COC (Bluetooth Low Energy connection-oriented channels). Samsung and Sony phones on Android 15 are not affected - this is specific to Fairphone's implementation.

This has been reported to both Fairphone and Abbott (FreeStyle) but neither has released a fix. Please also report it to:
- **Fairphone:** https://forum.fairphone.com
- **Abbott:** https://www.freestylelibre.com/support
- **UK MHRA (medical device regulator):** https://yellowcard.mhra.gov.uk

### Credits

- **[Wanna_Winn](https://forum.fairphone.com/u/Wanna_Winn)** - identified the ADB fix approach on the [Fairphone Community Forum](https://forum.fairphone.com/t/fp4-diabetesmanagment-mit-der-app-camaps-fx-probleme-nach-a15-upgrade/127146/28)
- **[Claude AI (Anthropic)](https://claude.ai)** - developed and extended the fix, built this tool
- Fairphone community forum threads:
  - [Bluetooth problems since Android 15 update](https://forum.fairphone.com/t/bluetooth-problems-since-android-15-update/127155)
  - [FreeStyle Libre 3 no longer working after upgrade to Android 15](https://forum.fairphone.com/t/freestyle-libre-3-no-longer-working-after-upgrade-to-android15/128464)

---

## Building from source

```bash
# Install dependencies
pip install pyinstaller

# Download Android Platform Tools and place adb.exe, AdbWinApi.dll,
# AdbWinUsbApi.dll in this directory, then:

python embed_adb.py   # embeds ADB into the app
python build.py       # creates dist/LibreFix.exe
```

---

*Not affiliated with Abbott, FreeStyle, or Fairphone. Use at your own risk.*
