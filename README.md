# LibreFix

**One-click fix for FreeStyle Libre Bluetooth on Fairphone after the Android 15 update.**

After the March/April 2026 Android 15 update on Fairphone 4 and 5, FreeStyle LibreLink loses its Bluetooth connection to Libre sensors. NFC manual scanning still works but continuous glucose monitoring stops. The app shows "Ready to scan" instead of live readings.

---

## Important - Please Read First

**The underlying fix (the ADB commands) has been tested and confirmed working on one Fairphone 5 running FP5.VT2Q.**

**The LibreFix.exe application is experimental and has not been widely tested.** We are releasing it in good faith and asking the community to help verify it works. Please report back in the issues whether it worked for you or not.

**Use entirely at your own risk.** This is not affiliated with Abbott, FreeStyle, or Fairphone. It is a community tool built by people trying to help other people.

If you are not comfortable running an untested .exe, the manual ADB commands that we know work are documented in the [Reddit post](https://www.reddit.com/r/fairphone/comments/1t2zz7w/fix_freestyle_libre_23_bluetooth_not_working_on/) and you can run those directly instead.

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

---

## Does it work?

The underlying ADB commands were tested on one Fairphone 5 running FP5.VT2Q (April 2026 update) with FreeStyle Libre 2, and worked for 5+ hours after applying.

The .exe itself is experimental - we need community testing to confirm it works across different devices and setups. **Please open an issue to report whether it worked for you**, including your Fairphone model, Android version, and Libre sensor model.

---

## Does it need root?

No. LibreFix uses ADB (Android Debug Bridge) which only requires USB Debugging to be enabled. No rooting required.

If the .exe doesn't work for you, a more comprehensive manual fix (including a rooting option as a last resort) is documented in the Reddit post linked above.

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

## Important after fixing

- Do not accept Fairphone OTA updates until Fairphone officially fixes the Bluetooth bug - an update may undo this fix
- If you replace your sensor, you may need to run LibreFix again
- If the connection drops, try toggling Bluetooth off and on, then run LibreFix again

---

## Supported devices

- Fairphone 4 (Android 15) - untested, please report back
- Fairphone 5 (Android 15) - confirmed working on FP5.VT2Q

## Supported LibreLink regions

Automatically detects your regional version:
UK, France, Germany, USA, Netherlands, Belgium, Spain, Italy, Sweden, Norway, Denmark, Finland, Australia, Canada.

If your region isn't listed, open an issue - we just need your package name (run `adb shell pm list packages | grep -i libre` to find it).

---

## Please help by reporting back

This is a community project. The more people who report results, the more confident others can be. Please open a GitHub issue with:
- Did it work? Yes/No
- Fairphone model and Android version
- Libre sensor model (Libre 2, Libre 2+, Libre 3)
- LibreLink region/version
- Any errors you saw

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
pip install pyinstaller

# Download Android Platform Tools and place adb.exe, AdbWinApi.dll,
# AdbWinUsbApi.dll in this directory, then:

python embed_adb.py   # embeds ADB into the app
python build.py       # creates dist/LibreFix.exe
```

---

*Not affiliated with Abbott, FreeStyle, or Fairphone. Experimental community tool. Use at your own risk.*
