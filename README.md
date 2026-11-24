# 🌬️ Vestel Smart Life — Home Assistant Integration

<p align="center">
  <a href="#english">🇬🇧 English</a>
  &nbsp; | &nbsp;
  <a href="#türkçe">🇹🇷 Türkçe</a>
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=Vestel_Smart_Life&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Install with HACS">
  </a>
  &nbsp;
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=vestel_smart_life">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Add to Home Assistant">
  </a>
</p>

---

<a id="english"></a>

# 🇬🇧 English

Vestel Smart Life is an unofficial Home Assistant custom integration for devices in the Vestel Smart Life / Evin Aklı app. Air conditioners (Doğa / Flora series) and refrigerators can be controlled; washing machines, dryers, dishwashers, ovens and fridge-freezers are shown read only.

> **Upgrading from 1.0.x ("Vestel AC")?** The integration now has its own domain, `vestel_smart_life`. Remove the old *Vestel AC* entry, install this version and add *Vestel Smart Life* again. Entity IDs change.

It communicates directly with the Vestel Smart Life cloud API and provides advanced controls that are not normally exposed by Home Assistant.

> ⚠️ This is an unofficial community project and is not affiliated with Vestel.

> **Tested on:** one air conditioner (variant `FLORA#MELTEM`, Wi-Fi card `HM07`). Other models should work for the common controls but are untested; please attach the diagnostics when reporting a problem. Refrigerator support (see below) is new and has not been tried on a real refrigerator yet; other appliance families are read only and untested too.

## ✨ Features

- 🌡️ Cooling, heating, dry, fan-only and auto modes
- 🎯 Target temperature control
- 🌀 Auto + 1-5 fan speeds
- ↕️ Vertical louver position control
- 🔄 Vertical swing / stop swing
- ⚡ Turbo mode
- 🌙 Sleep mode
- 🍃 Eco / Energy Saving mode
- ✨ Ionizer
- ⏰ Automatic shutdown timer
- 🩺 Diagnostic information
- 🌫️ VOC / particle air-quality information on supported models
- 🧹 Filter / particle-sensor lifetime information where available
- 🧊 Refrigerators: door, temperatures, modes, child lock, screen saver
- 🏠 Washing machines, dryers, dishwashers, ovens and fridge-freezers: state, program, remaining time and errors (read only)
- 🧪 Raw API status and command services
- 🔐 Automatic authentication with Vestel account credentials
- 📡 Live state: changes made with the remote control or the app show up within seconds

---

## 🚀 Installation

### HACS — Recommended

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=Vestel_Smart_Life&category=integration">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Install with HACS">
</a>

Or manually:

1. Open HACS → Integrations.
2. Open ⋮ → Custom repositories.
3. Add:

    https://github.com/mutlutekir/Vestel_Smart_Life

4. Select **Integration**.
5. Install **Vestel Smart Life**.
6. Restart Home Assistant.

### Manual

Download the latest release and copy:

    custom_components/vestel_smart_life

to:

    /config/custom_components/

Then restart Home Assistant.

---

## ⚙️ Configuration

Go to:

    Settings → Devices & Services → Add Integration

Search for:

    Vestel Smart Life

The integration supports:

- Username / password login
- Refresh-token authentication as a fallback

After authentication, the Vestel devices on your account (air conditioners, refrigerators and the other appliances) are discovered automatically.

---

## 🎛️ Supported Controls

| Feature | Support |
|---|:---:|
| Auto | ✅ |
| Cooling | ✅ |
| Heating | ✅ |
| Dry | ✅ |
| Fan Only | ✅ |
| Off | ✅ |
| Target Temperature | ✅ |
| Fan Auto / 1-5 | ✅ |
| Vertical Louver | ✅ |
| Vertical Swing | ✅ |
| Horizontal Louver | ❌ Not yet (encoding unconfirmed) |
| Turbo | ✅ |
| Sleep | ✅ |
| Eco | ✅ |
| Ionizer | ✅ |
| Auto Off Timer | ✅ |
| Diagnostics | ✅ |
| VOC / PM | ⚠️ Model dependent |
| Filter Lifetime | ⚠️ Model dependent |

---

## 🔬 Reverse-Engineered Parameters

The following values were identified from the Vestel Smart Life APK and verified against a real air conditioner.

### ACCMODE

| Value | Mode |
|---:|---|
| `0` | Auto |
| `1` | Cooling |
| `2` | Dry |
| `3` | Fan Only |
| `4` | Heating |
| `5` | Off |

### ACGENSI

The mode and fan speed are combined using:

    ACGENSI = ACCMODE + FanSpeed × 8

### ACFANPO

`ACFANPO` contains several settings as bit fields:

| Bits | Function |
|---|---|
| 0 | Turbo |
| 1-3 | Vertical louver |
| 4-6 | Horizontal louver (unconfirmed, read-only) |
| 7 | Sleep |
| 8 | Ionizer |
| 9 | Eco |

Vertical louver values:

| Value | Position |
|---:|---|
| `0` | Stop |
| `1` | Position 1 |
| `2` | Position 2 |
| `3` | Position 3 |
| `4` | Position 4 |
| `5` | Position 5 |
| `6` | Swing |

### Verified Vertical Louver Values

| Function | ACFANPO |
|---|---:|
| Top position | `00050` |
| Position 2 | `00052` |
| Position 3 | `00054` |
| Position 4 | `00056` |
| Bottom position | `00058` |
| Swing | `00060` |
| Stop / fixed position | `00048` |

### Verified Special Modes

| Function | Value |
|---|---:|
| Normal | `00050` |
| Sleep | `00178` |
| Ionizer | `00306` |
| Eco | `00562` |

Turbo is reflected in the `ACGENSI` state and was observed as:

    ACGENSI = 00025

---

## 📡 Live State

The unit publishes a message to Vestel's cloud whenever something changes (remote control,
buttons, the app, Home Assistant). The integration listens to those messages, the same way the
official app does, so the card follows the real state within seconds. This needs the
`paho-mqtt` package, which Home Assistant installs for the integration automatically.

The cloud's status document (polled every minute) stays as a fallback: it can be minutes
behind and does not report an on/off change reliably. If the live connection cannot be
opened, the integration logs one warning and keeps polling.

---

## ⏰ Automatic Shutdown

`ACOFFTV` stores the automatic shutdown time:

    ACOFFTV = (minutes << 5) | hours

The value:

    2047

means the timer is disabled.

Example:

    14:18 → 00590

The value is a clock time, and the unit cannot learn the time on its own. So, like the official app, the integration first sets the unit's clock to Home Assistant's local time (`ACSTCLK`) and then sends the shutdown time.

---

## 🧊 Refrigerators

Vestel refrigerators (device type `RF`) on the same account are discovered too. The registers and their packing come from the Smart Life app's own code and the sample documents bundled in it.

| Entity | Register | Notes |
|---|---|---|
| Door (binary sensor) | `RFDOORA` | Open for any value other than `3` (both closed), as the app does. Which door is open is not exposed; the raw value is an attribute. |
| Cooler / freezer temperature (select) | `RFTEMSE` | `(cooler °C << 8) \| abs(freezer °C)`. Choices: cooler 2, 4, 5, 6, 8 °C; freezer -16, -18, -20, -22, -24 °C. |
| Mode (select) | `RFMODEA` | Normal, Super Freeze, Super Cooler, Holiday, Eco, AI. One at a time; your model may not support all of them. |
| Child lock, Screen saver (switch) | `RFCLOCK`, `RFSSAVE` | 0 / 1. |
| Raw registers (diagnostic sensors, off by default) | all | Enable them to see what a button changes. |

> ⚠️ **Not yet verified on a real refrigerator.** Reading is cross-checked with observations from a real fridge ([tmturk2010](https://github.com/tmturk2010), PR #1 — thank you); the commands are built exactly as the app builds them, but nobody has confirmed them on hardware. Please try one change at a time, watch the fridge's own display, and report what happened. Refrigerators are polled (no live messages yet), so the door sensor can be about a minute late.

---

## 🏠 Other appliances (read only)

Washing machines (`WM`), washer-dryers (`WD`), tumble dryers (`TD`), dishwashers (`DW`), ovens (`OV`) and fridge-freezers (`FD`) on the account are discovered as well and show what the app shows: state, selected program, remaining time, door, remote control, child lock and errors (a "problem" sensor lists the active errors). Values come from the register tables the Smart Life app ships for each family (`tools/extract_registers.py` rebuilds them).

- **Read only on purpose.** The app's commands for these appliances start programs; starting a wash or heating an oven from Home Assistant has not been tried and is left out. The `send_raw_code` service is still there for experiments.
- **Not verified on real appliances.** Value names are the app's own (English); tell me what looks wrong. Sensor temperatures of fridge-freezers (`FD`) are decoded as signed numbers, which is a guess.
- Polled about once a minute.

---

## 🩺 Diagnostic Data

The APK exposes additional diagnostic fields. Availability depends on the air-conditioner model and firmware.

| Field | Description |
|---|---|
| `ACERROR` | Error information |
| `ACERRTW` | UVC / particle sensor errors |
| `ACWARNG` | Warning information |
| `ACPOLVC` | VOC air quality |
| `ACPOLPM` | Particle / PM air quality |
| `ACOAFLP` | Odor & allergen filter lifetime |
| `ACPSCLP` | Particle sensor lifetime |
| `ACSAFRS` | Filter / sensor reset |
| `ACVERSI` | Firmware information |

Some fields may not be returned by the device. Missing capabilities are therefore not considered an error.

> ℹ️ In 2.0.0 the status comes from Vestel's newer status document plus the unit's live messages. The VOC, particle, filter-lifetime and UVC fields above are only filled where that document provides them; on models that publish them only as raw registers they stay empty. Reading those registers again is planned.

---

## 🧪 Raw API Services

For advanced testing and feature discovery, the integration provides raw API services.

### Dump current device status

    vestel_smart_life.dump_raw_status

### Send a raw command

    vestel_smart_life.send_raw_code

Example:

    action: vestel_smart_life.send_raw_code
    data:
      code: "ACFANPO00562"

These services are mainly intended for development and reverse engineering.

> ⚠️ Do not send unknown values to the device. Incorrect commands may change its operating state.

**Own one of the other appliances?** [`docs/device-testing.md`](docs/device-testing.md) lists the codes worth trying on a refrigerator, washing machine, dryer, dishwasher and so on, what each should do, and how to report the result by opening an issue.

---

## 🔍 Feature Discovery

New features can be investigated by comparing the raw status before and after changing a setting in the official Vestel application.

Recommended workflow:

    dump_raw_status
          ↓
    Change one setting
          ↓
    dump_raw_status
          ↓
    Compare changed fields
          ↓
    Test the discovered value
          ↓
    Add the feature to Home Assistant

---

## ❤️ Credits

- Developed and maintained by **Mutlu Tekir**.
- Refrigerator observations: **tmturk2010**
- Inspired by **Sezer İltekin**'s vestel-ac-remote-control web-panel.
Sezer İltekin's project was an early public exploration of the Vestel cloud. The API client in this integration is a separate, new implementation: it is written from the Vestel Smart Life app's own code (APK analysis) and from responses observed on a real account, and no code was taken from that project. See `docs/protocol.md` for the sources.
- Licensed under GPL-3.0, see [LICENSE](LICENSE).

---

## ⚠️ Disclaimer

This project is unofficial and is not affiliated with Vestel.

The integration relies on the Vestel cloud API. API changes, authentication changes or service shutdowns by Vestel may cause the integration to stop working.

Some features are model and firmware dependent.

If you encounter a problem, please open an issue:

https://github.com/mutlutekir/Vestel_Smart_Life/issues

Do not include passwords, access tokens or refresh tokens in issue reports.

---

<a id="türkçe"></a>

# 🇹🇷 Türkçe

Vestel Smart Life, Vestel Smart Life / Evin Aklı uygulamasındaki cihazları Home Assistant üzerinden kontrol etmek için geliştirilmiş resmi olmayan bir özel entegrasyondur. Klimalar ve buzdolapları kontrol edilebiliyor; çamaşır makinesi, kurutma makinesi, bulaşık makinesi, fırın ve buzdolabı-dondurucu salt okunur gösteriliyor.

> **1.0.x ("Vestel AC") sürümünden mi geliyorsun?** Entegrasyonun yeni bir alan adı var: `vestel_smart_life`. Eski *Vestel AC* girdisini sil, bu sürümü kur ve *Vestel Smart Life*'ı yeniden ekle. Entity kimlikleri değişir.

Vestel Akıllı Yaşam bulut API'si ile doğrudan iletişim kurar ve Home Assistant'ta normalde bulunmayan gelişmiş kontrolleri sunar.

> ⚠️ Bu proje resmi değildir ve Vestel ile herhangi bir bağlantısı yoktur.

> **Test edilen:** tek bir klima (varyant `FLORA#MELTEM`, Wi-Fi kartı `HM07`). Diğer modellerde ortak kontroller çalışmalı ama test edilmedi; sorun bildirirken tanı verisini (diagnostics) ekle. Buzdolabı desteği (aşağıya bak) yenidir ve henüz gerçek bir buzdolabında denenmedi; diğer cihaz aileleri salt okunurdur ve onlar da test edilmedi.

## ✨ Özellikler

- 🌡️ Soğutma, ısıtma, nem alma, fan ve otomatik mod
- 🎯 Hedef sıcaklık kontrolü
- 🌀 Auto + 1-5 fan hızı
- ↕️ Dikey kanatçık pozisyonu
- 🔄 Dikey salınım / salınımı durdurma
- ⚡ Turbo
- 🌙 Uyku
- 🍃 Tasarruf / Eco
- ✨ İyonizer
- ⏰ Otomatik kapatma zamanlayıcısı
- 🩺 Tanı / hata bilgileri
- 🌫️ Desteklenen modellerde VOC / partikül hava kalitesi
- 🧹 Desteklenen modellerde filtre / partikül sensörü ömrü
- 🧊 Buzdolabı: kapı, sıcaklıklar, modlar, çocuk kilidi, ekran koruyucu
- 🏠 Çamaşır makinesi, kurutma makinesi, bulaşık makinesi, fırın ve buzdolabı-dondurucu: durum, program, kalan süre ve hatalar (salt okunur)
- 🧪 Ham API durum ve komut servisleri
- 🔐 Vestel hesabıyla otomatik kimlik doğrulama
- 📡 Canlı durum: kumanda ya da uygulamadan yapılan değişiklikler birkaç saniyede görünür

---

## 🚀 Kurulum

### HACS — Önerilen

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=Vestel_Smart_Life&category=integration">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="HACS ile yükle">
</a>

Alternatif olarak:

1. Home Assistant'ta HACS → Integrations bölümünü açın.
2. Sağ üstten ⋮ → Custom repositories seçin.
3. Aşağıdaki adresi ekleyin:

    https://github.com/mutlutekir/Vestel_Smart_Life

4. Kategori olarak **Integration** seçin.
5. **Vestel Smart Life** entegrasyonunu yükleyin.
6. Home Assistant'ı yeniden başlatın.

### Manuel

Son sürümü indirin ve:

    custom_components/vestel_smart_life

klasörünü:

    /config/custom_components/

içine kopyalayın.

Ardından Home Assistant'ı yeniden başlatın.

---

## ⚙️ Yapılandırma

Şuraya gidin:

    Ayarlar → Cihazlar ve Hizmetler → Entegrasyon Ekle

Aratın:

    Vestel Smart Life

Kimlik doğrulama için:

- Kullanıcı adı / şifre
- Yedek olarak Refresh Token

kullanılabilir.

Kimlik doğrulama tamamlandıktan sonra hesabındaki Vestel cihazlar (klimalar, buzdolapları ve diğer cihazlar) otomatik olarak keşfedilir.

---

## 🎛️ Desteklenen Kontroller

| Özellik | Destek |
|---|:---:|
| Otomatik | ✅ |
| Soğutma | ✅ |
| Isıtma | ✅ |
| Nem Alma | ✅ |
| Sadece Fan | ✅ |
| Kapalı | ✅ |
| Hedef Sıcaklık | ✅ |
| Fan Auto / 1-5 | ✅ |
| Dikey Kanatçık | ✅ |
| Dikey Salınım | ✅ |
| Yatay Kanatçık | ❌ Henüz yok (kodlama doğrulanmadı) |
| Turbo | ✅ |
| Uyku | ✅ |
| Tasarruf | ✅ |
| İyonizer | ✅ |
| Otomatik Kapatma | ✅ |
| Tanı Bilgileri | ✅ |
| VOC / PM | ⚠️ Modele bağlı |
| Filtre Ömrü | ⚠️ Modele bağlı |

---

## 🔬 Çözümlenen Parametreler

Bu değerler Vestel Akıllı Yaşam APK'sından araştırılmış ve gerçek bir klima üzerinde doğrulanmıştır.

### ACCMODE

| Değer | Mod |
|---:|---|
| `0` | Otomatik |
| `1` | Soğutma |
| `2` | Nem Alma |
| `3` | Sadece Fan |
| `4` | Isıtma |
| `5` | Kapalı |

### ACGENSI

Mod ve fan hızı birlikte kodlanır:

    ACGENSI = ACCMODE + FanSpeed × 8

### ACFANPO

| Bitler | Özellik |
|---|---|
| 0 | Turbo |
| 1-3 | Dikey kanatçık |
| 4-6 | Yatay kanatçık (doğrulanmadı, salt okunur) |
| 7 | Uyku |
| 8 | İyonizer |
| 9 | Tasarruf |

Dikey kanatçık:

| Değer | Pozisyon |
|---:|---|
| `0` | Durdur |
| `1` | 1. kademe |
| `2` | 2. kademe |
| `3` | 3. kademe |
| `4` | 4. kademe |
| `5` | 5. kademe |
| `6` | Salınım |

### Doğrulanmış Dikey Kanatçık Değerleri

| İşlev | ACFANPO |
|---|---:|
| En üst | `00050` |
| 2. kademe | `00052` |
| 3. kademe | `00054` |
| 4. kademe | `00056` |
| En alt | `00058` |
| Salınım | `00060` |
| Salınımı durdur | `00048` |

### Doğrulanmış Özel Modlar

| İşlev | Değer |
|---|---:|
| Normal | `00050` |
| Uyku | `00178` |
| İyonizer | `00306` |
| Tasarruf | `00562` |

Turbo için gerçek cihazda:

    ACGENSI = 00025

değeri gözlemlenmiştir.

---

## 📡 Canlı Durum

Cihaz, bir şey değiştiğinde (kumanda, tuşlar, uygulama, Home Assistant) Vestel bulutuna mesaj yayınlar. Entegrasyon resmi uygulama gibi bu mesajları dinler; böylece kart gerçek durumu birkaç saniye içinde gösterir. Bunun için `paho-mqtt` paketi gerekir, Home Assistant bunu entegrasyon için otomatik kurar.

Bulutun durum belgesi (dakikada bir sorgulanır) yedek olarak durur: dakikalarca geride kalabilir ve aç/kapa değişikliğini güvenilir bildirmez. Canlı bağlantı açılamazsa entegrasyon bir uyarı yazar ve sorgulamaya devam eder.

---

## ⏰ Otomatik Kapatma

`ACOFFTV` otomatik kapanma saatini tutar:

    ACOFFTV = (dakika << 5) | saat

    2047 = zamanlayıcı kapalı

Örneğin:

    14:18 → 00590

Değer bir saat bilgisidir ve cihaz saati kendi başına öğrenemez. Bu yüzden entegrasyon, resmi uygulama gibi, önce cihazın saatini Home Assistant'ın yerel saatine ayarlar (`ACSTCLK`), sonra kapanma saatini gönderir.

---

## 🧊 Buzdolapları

Aynı hesaptaki Vestel buzdolapları (cihaz tipi `RF`) de bulunur. Kayıtlar ve paketleme biçimi Smart Life uygulamasının kendi kodundan ve içindeki örnek belgelerden alınmıştır.

| Varlık | Kayıt | Notlar |
|---|---|---|
| Kapı (binary sensor) | `RFDOORA` | `3` (ikisi de kapalı) dışındaki her değerde açık, uygulama da böyle yapar. Hangi kapının açık olduğu gösterilmez; ham değer nitelik olarak yer alır. |
| Soğutucu / dondurucu sıcaklığı (select) | `RFTEMSE` | `(soğutucu °C << 8) \| mutlak(dondurucu °C)`. Seçenekler: soğutucu 2, 4, 5, 6, 8 °C; dondurucu -16, -18, -20, -22, -24 °C. |
| Mod (select) | `RFMODEA` | Normal, Süper Dondurma, Süper Soğutma, Tatil, Ekonomi, Yapay Zeka. Aynı anda biri; modeliniz hepsini desteklemeyebilir. |
| Çocuk kilidi, Ekran koruyucu (switch) | `RFCLOCK`, `RFSSAVE` | 0 / 1. |
| Ham kayıtlar (tanı sensörleri, varsayılan kapalı) | hepsi | Bir tuşun neyi değiştirdiğini görmek için açın. |

> ⚠️ **Gerçek bir buzdolabında henüz doğrulanmadı.** Okuma kısmı gerçek bir buzdolabından yapılan gözlemlerle ([tmturk2010](https://github.com/tmturk2010), PR #1 — teşekkürler) karşılaştırıldı; komutlar uygulamanın kurduğu biçimde oluşturuluyor, ancak donanımda kimse denemedi. Lütfen her seferinde tek değişiklik deneyin, buzdolabının kendi ekranına bakın ve sonucu bildirin. Buzdolapları periyodik sorgulanır (canlı mesaj yok), kapı sensörü yaklaşık bir dakika gecikebilir.

---

## 🏠 Diğer cihazlar (salt okunur)

Hesaptaki çamaşır makineleri (`WM`), kurutmalı çamaşır makineleri (`WD`), kurutma makineleri (`TD`), bulaşık makineleri (`DW`), fırınlar (`OV`) ve buzdolabı-dondurucular (`FD`) de bulunur ve uygulamanın gösterdiklerini gösterir: durum, seçili program, kalan süre, kapak, uzaktan kontrol, çocuk kilidi ve hatalar ("Hata Var" sensörü etkin hataları listeler). Değerler, Smart Life uygulamasının her aile için içinde taşıdığı kayıt tablolarından gelir (`tools/extract_registers.py` bunları yeniden üretir).

- **Bilerek salt okunur.** Uygulamanın bu cihazlar için komutları program başlatır; Home Assistant'tan yıkama başlatmak ya da fırını ısıtmak denenmedi ve dışarıda bırakıldı. Deneme için `send_raw_code` servisi duruyor.
- **Gerçek cihazlarda doğrulanmadı.** Değer adları uygulamanın kendi (İngilizce) adlarıdır; yanlış görünen bir şey varsa bildirin. Buzdolabı-dondurucu (`FD`) sensör sıcaklıkları işaretli sayı olarak çözülür, bu bir tahmindir.
- Yaklaşık dakikada bir sorgulanır.

---

## 🩺 Tanı Bilgileri

APK içerisinde aşağıdaki alanlar tespit edilmiştir. Kullanılabilirlik klima modeline ve firmware'e bağlıdır.

| Alan | Açıklama |
|---|---|
| `ACERROR` | Hata bilgisi |
| `ACERRTW` | UVC / partikül sensörü hatası |
| `ACWARNG` | Uyarı |
| `ACPOLVC` | VOC hava kalitesi |
| `ACPOLPM` | Partikül / PM hava kalitesi |
| `ACOAFLP` | Koku & alerjen filtre ömrü |
| `ACPSCLP` | Partikül sensörü ömrü |
| `ACSAFRS` | Filtre / sensör sıfırlama |
| `ACVERSI` | Firmware bilgisi |

Bazı cihazlarda bu alanlar hiç bulunmayabilir. Bu durumda ilgili özelliklerin kullanılamaması normaldir.

> ℹ️ 2.0.0 sürümünde durum, Vestel'in yeni durum belgesinden ve cihazın canlı mesajlarından gelir. Yukarıdaki VOC, partikül, filtre ömrü ve UVC alanları yalnızca bu belgenin verdiği yerlerde dolar; bunları yalnızca ham kayıt olarak yayınlayan modellerde boş kalır. Bu kayıtların yeniden okunması planlanıyor.

---

## 🧪 Ham API Servisleri

### Cihazın ham durumunu görüntüleme

    vestel_smart_life.dump_raw_status

### Ham komut gönderme

    vestel_smart_life.send_raw_code

Örnek:

    action: vestel_smart_life.send_raw_code
    data:
      code: "ACFANPO00562"

Bu servisler özellikle yeni özelliklerin araştırılması için kullanılabilir.

> ⚠️ Ne yaptığını bilmediğiniz değerleri cihaza göndermeyin.

**Diğer cihazlardan birine mi sahipsin?** [`docs/device-testing.md`](docs/device-testing.md) buzdolabı, çamaşır makinesi, kurutma makinesi, bulaşık makinesi vb. için denenmeye değer kodları, her birinin ne yapması gerektiğini ve sonucu issue açarak nasıl bildireceğini listeler.

## 🔍 Yeni Özellik Keşfetme

Resmi uygulamadaki bir özelliği araştırmak için:

    dump_raw_status
          ↓
    Uygulamadan özelliği değiştir
          ↓
    dump_raw_status
          ↓
    Değişen alanı bul
          ↓
    Değeri test et
          ↓
    Home Assistant'a ekle

Bu yöntemle dikey kanatçık, salınım, Turbo, Uyku, İyonizer, Tasarruf, Fan modu ve zamanlayıcı gibi birçok özellik keşfedilmiştir.

---

## ❤️ Emeği Geçenler

- Geliştiren ve sürdüren: **Mutlu Tekir**.
- Buzdolabı gözlemleri: **tmturk2010**
- **Sezer İltekin**'in vestel-ac-remote-control web-panelinden esinlenilmiştir.
Sezer İltekin'in projesi Vestel bulutunun ilk herkese açık keşiflerinden biriydi. Bu entegrasyondaki API istemcisi ayrı ve yeni bir uygulamadır: Vestel Smart Life uygulamasının kendi kodundan (APK analizi) ve gerçek bir hesapta gözlenen yanıtlardan yazılmıştır, o projeden kod alınmamıştır. Kaynaklar için `docs/protocol.md` dosyasına bak.
- GPL-3.0 lisansıyla dağıtılır, bkz. [LICENSE](LICENSE).

---

## ⚠️ Yasal Uyarı

Bu proje resmi değildir ve Vestel ile bağlantılı değildir.

Entegrasyon Vestel'in bulut API'sine bağlıdır. API, kimlik doğrulama sistemi veya servis tarafında yapılacak değişiklikler entegrasyonun çalışmasını engelleyebilir.

Bazı özellikler cihaz modeli ve firmware sürümüne bağlıdır.

Sorun yaşarsanız:

https://github.com/mutlutekir/Vestel_Smart_Life/issues

üzerinden issue açabilirsiniz.

> 🔒 Şifre, access token veya refresh token gibi bilgileri issue içerisinde paylaşmayın.

---

<p align="center">
  🌬️ <strong>Vestel Smart Life + Home Assistant</strong>
  <br>
  <sub>Unofficial Community Integration</sub>
</p>
