# Device test guide · Cihaz deneme rehberi

[🇬🇧 English](#english) · [🇹🇷 Türkçe](#türkçe)

---

<a id="english"></a>

# 🇬🇧 English

Only air conditioners have been verified on real hardware. Refrigerators have control entities,
and the other appliances (washing machine, washer-dryer, dryer, dishwasher, oven, fridge-freezer)
are read only. All of it was worked out from the Smart Life app, **not tested on the devices**.

If you own one of these appliances you can help: send the codes below with the
`vestel_smart_life.send_raw_code` service, watch what the appliance does, and
[open an issue](https://github.com/mutlutekir/Vestel_Smart_Life/issues/new?template=device-test-report.yml)
with the result. A single line such as "`WMUISET01283` → the display showed 40 °C / 1000 rpm" is already useful.
"Nothing happened" is a useful result too.

## Safety first

- **You are responsible for what you send.** These codes are what the official app sends, but the
  integration has never sent them to your model.
- Test only what you can watch. For a washing machine, dryer or dishwasher: **empty machine, you
  are in the room, water and drain connected.** Keep your finger near the stop button on the unit.
- Each code has a level:
  - 🟢 harmless: a switch or a display setting, nothing starts.
  - 🟡 changes a setting (program, temperature, mode, delay). Nothing starts. Put the old value back afterwards.
  - 🔴 starts, pauses or stops a program. Supervised, empty machine only.
- **Ovens:** please do not send a start or a heating command. Only the observations and the 🟢 stop/off
  codes are asked for. The other oven codes are listed so reports can refer to them.
- **Fridges:** do not switch a zone off, and put the temperature back after the test, so the food stays safe.
- Do not send values that are not in the tables. Nobody has tried them, and a wrong value may leave the appliance in a state only a power cycle fixes.

## How to test

1. Open **Developer tools → Actions** and pick `vestel_smart_life.dump_raw_status` (listed as
   "Ham durumu göster (debug)"), choose the appliance, run it. A notification shows every register.
   Copy it: this is the **before** state.
2. Send one code:

   ```yaml
   action: vestel_smart_life.send_raw_code
   data:
     device_id: <pick the appliance in the UI>
     code: "RFCLOCK00001"
   ```

   A code is the 7-letter register name followed by a 5-digit number, no spaces.
3. Wait about 10 seconds (the cloud can be slow), then run `dump_raw_status` again. This is the **after** state.
   Do not rely on the entities for this: appliances other than air conditioners refresh every 30 seconds.
4. Look at the appliance and at the Smart Life app. Did the display change? Did the app follow?
5. Put the old value back, then go on with the next code. One code at a time.

## Observations (no commands needed)

These help the most and cost nothing. Run `dump_raw_status` in each state and note the registers that changed.

| Appliance | What to do | What we learn |
|---|---|---|
| Refrigerator | Open **only the fridge door**, dump. Close it. Open **only the freezer door**, dump. Open both, dump. | What `RFDOORA` means for 0, 1 and 2 (the sample document and one report disagree). |
| Refrigerator | Read `RFTEMSE` while the unit shows a known setpoint. | Confirms cooler and freezer values. |
| Fridge-freezer | Compare the temperature registers (names ending in `TE`) with the unit's display. | Their encoding (we guess signed numbers). |
| Washer, washer-dryer, dryer, dishwasher | Idle, program chosen, running, paused, door open, finished. Dump each time. | The state, step and error registers. |
| Washer, dryer, dishwasher | Set a delay of e.g. 3 hours in the app, then dump. | Whether the delay registers count minutes or hours. |
| Any | If a fault ever shows up on its own, dump while it is displayed. | Which error bit or code is which. |

## Refrigerator (`RF`)

The integration already has entities for these (child lock, screen saver, mode, temperatures).
Try the entities first. The raw codes are for comparison and for the registers without an entity.

| Code | Should do | Level |
|---|---|---|
| `RFCLOCK00001` / `RFCLOCK00000` | Child lock on / off | 🟢 |
| `RFSSAVE00001` / `RFSSAVE00000` | Screen saver on / off | 🟢 |
| `RFMODEA00000` | Normal mode | 🟡 |
| `RFMODEA00002` | Super freeze | 🟡 |
| `RFMODEA00004` | Super cooler | 🟡 |
| `RFMODEA00008` | Holiday | 🟡 |
| `RFMODEA00016` | Eco (not listed in the sample, may be model dependent) | 🟡 |
| `RFMODEA00032` | AI mode | 🟡 |
| `RFTEMSE01042` | Cooler 4 °C and freezer −18 °C | 🟡 |
| `RFTEMSE00536` | Cooler 2 °C and freezer −24 °C | 🟡 |
| `RFTEMSE02064` | Cooler 8 °C and freezer −16 °C | 🟡 |
| `RFDCOOL00001` | Quick drink cooling (state in the sample: 0 open, 1 closed, 2 finished). We do not know whether this register is writable. | 🟡 |

`RFTEMSE` = cooler × 256 + freezer (freezer without the minus sign). Cooler: 2, 4, 5, 6, 8.
Freezer: 16, 18, 20, 22, 24. Only one mode is active at a time.

## Fridge-freezer (`FD`)

Each setting is a register that holds one number. Which zone is which depends on the model:
the zone whose list goes 1–8 is the chilled one, the other is the freezer. Never send `00000` (off).

| Code | Should do | Level |
|---|---|---|
| `FDMAINA00001` … `FDMAINA00008` | Main compartment 1 … 8 °C | 🟡 |
| `FDMAINA00009` | Super cool | 🟡 |
| `FDZONE1` / `FDZONE2` with 1 … 8 | Chilled zone 1 … 8 °C (`FDZONE1` 9 = VitaStore on models with it) | 🟡 |
| `FDZONE1` with 10 … 20 | Freezer zone −14 … −24 °C (10 = −14, 11 = −15, …, 20 = −24); 21 = super freeze | 🟡 |
| `FDZONE2` with 9 … 19 | Freezer zone −14 … −24 °C (9 = −14, 10 = −15, …, 19 = −24); 20 = super freeze | 🟡 |
| `FDMODE2` with 0 / 1 / 2 | No mode / Eco / Holiday | 🟡 |

Example: `FDZONE200013` on a model whose zone 2 is the freezer = −18 °C. Say in your report which of the two zones changed.

## Washing machine (`WM`)

Empty drum, door closed, you are watching. Program numbers differ between models: take the
list the app shows and compare it with the table (sample model T225).

| Code | Should do | Level |
|---|---|---|
| `WMFORPR00003` | Select program Cotton | 🟡 |
| `WMFORPR00019` / `00002` / `00005` / `00004` / `00007` / `00008` | Eco 40-60 / Cotton prewash / Cotton 20 / Colours / Wool / Rinse | 🟡 |
| `WMFORPR00016` / `00009` / `00010` / `00006` / `00012` / `00013` / `00014` / `00015` | Allergy safe / Spin+drain / Handwash shirt / Easycare outdoor / Duvet / Curtain / Fast 60 / Rapid 15 | 🟡 |
| `WMUISET01283` | Temperature 40 °C and spin 1000 rpm | 🟡 |
| `WMUISET01026` | 30 °C and 800 rpm | 🟡 |
| `WMUISET00000` | Cold and no spin | 🟡 |
| `WMUISO1<n>` | Option bits: 2 = rapid wash, 1024 = mix. It is a bit field: read the current value in the raw status first and send the sum, otherwise other options are switched off. | 🟡 |
| `WMDELAY00060` | Delay of 60 (minutes or hours? please say what the display shows) | 🟡 |
| `WMDCPST00002` | Start with the delay that was set | 🔴 |
| `WMDCPST00001` | Start | 🔴 |
| `WMDCPST00003` | Pause | 🔴 |

`WMUISET` = temperature code + spin code × 256. Temperature: 0 cold, 1 = 20, 2 = 30, 3 = 40, 4 = 50, 5 = 60, 6 = 70, 7 = 80, 8 = 90 °C.
Spin: 0 none, 1 = 400, 3 = 600, 4 = 800, 5 = 1000, 6 = 1200 rpm.
`WMCANCL` (cancel) exists in the app but its value is not known; if you can see it in a capture, tell us.

## Washer-dryer (`WD`)

| Code | Should do | Level |
|---|---|---|
| `WDFORPR00019` | Select Eco 40-60 | 🟡 |
| `WDFORPR00002` / `00004` / `00005` / `00006` / `00007` / `00008` | Cotton / Cotton 20 / Synthetics / Wool-silk / Duvet / Rinse | 🟡 |
| `WDFORPR00012` / `00009` / `00011` / `00010` | Allergy safe / Spin+drain / Rapid 15 / Fast 60 | 🟡 |
| `WDFORPR00013` / `00014` / `00015` / `00016` | Dry delicate / Dry cotton / Dry jet wash / Dry cotton after 6 h wash | 🟡 |
| `WDUISET<n>` | Temperature + spin × 256, like the washing machine. Spin: 0 none, 1 = 400, 4 = 800, 5 = 1000, 6 = 1200, 7 = 1400 rpm. Temperature: 0 cold, 1 = 20, 2 = 30, 3 = 40, 5 = 60, 6 = 70, 7 = 80, 8 = 90. | 🟡 |
| `WDDRYOP00514` | Dry level 2 and 60 minutes (level + time × 256; level 0-3, time 0 none, 1 = 30, 2 = 60, 3 = 90, 4 = 120 min) | 🟡 |
| `WDUISO1<n>` | Option bits: 4 pre-wash, 8 easy iron, 16 extra rinse, 32 anti-allergy (bit field, see above) | 🟡 |
| `WDECOSP<n>` | Bits: 1 save plus, 2 speed | 🟡 |
| `WDDELAY00060` | Delay of 60 (unit?) | 🟡 |
| `WDDCPST00001` / `00002` / `00003` | Start / start with delay / pause | 🔴 |

## Dishwasher (`DW`)

| Code | Should do | Level |
|---|---|---|
| `DWPROSI00004` | Select Eco 50 | 🟡 |
| `DWPROSI00002` / `00003` / `00005` / `00006` / `00007` / `00008` / `00010` / `00017` / `00023` | Jetwash 14 / Quick 30 / Dual pro wash / Super 50 / Smart 30-50 / Smart 50-60 / Steam wash / Save 54 / Crystal light wash | 🟡 |
| `DWPROSI00000` | Reset | 🟡 |
| `DWFAVSS00001` | Select favourite 1 | 🟡 |
| `DWPROOP<n>` | Options, one bit each: 2 tablet, 8 upper spray, 16 lower spray, 32 extra fast, 64 extra silent, 128 auto door, 512 extra dry, 1024 extra hygiene. Send the sum, e.g. `DWPROOP00520` = extra dry (512) + upper spray (8). | 🟡 |
| `DWDFDEL00060` | Delay (the sample says minutes, step 60) | 🟡 |
| `DWPROST00001` | Start (running) | 🔴 |
| `DWPROST00002` | Pause | 🔴 |
| `DWPROST00000` | Back to the pre-program state | 🔴 |

Note: the options must be chosen in the pre-program state, and only some are allowed per program. Read the
current `DWPROOP` first and change one bit.

## Tumble dryer (`TD`)

| Code | Should do | Level |
|---|---|---|
| `TDCHLOC00001` / `TDCHLOC00000` | Child lock on / off | 🟢 |
| `TDBUZZR00001` / `TDBUZZR00000` | Buzzer on / off | 🟢 |
| `TDSELPR00001` | Select Cotton extra dry (value + a 2-bit field we do not know; keep it 0) | 🟡 |
| `TDSELPR00002` … | 2 cupboard dry, 3 iron dry, 4 synthetics cupboard, 5 synthetics iron, 6 delicate, 7 mix, 8 baby care, 14 refresh, 16 express, 19 shirts, 21 time drying, 22 duvet, 23 sport, 24 wool refresh | 🟡 |
| `TDDRYLV00002` | Dry level 2 (0-3) | 🟡 |
| `TDOPANT00001` / `00000` | Anti-crease (60 min) on / off | 🟡 |
| `TDOPDEL00001` | Delicate option | 🟡 |
| `TDOPION00001`, `TDOPUVC00001` | Ion / UV option (only on models that have it) | 🟡 |
| `TDTIDRY00060` | Time drying 60 min (20, 30, 40, 50, 60, 80 … 200); in the refresh program 10 … 120 | 🟡 |
| `TDDTIMR00060` | Delay (0 … 1380, step 60) | 🟡 |
| `TDSTART00001` | Start. The app code sends 1, the sample document says 2 | 🔴 |
| `TDSTART00002` | Start, if 1 did nothing. Please tell us which one worked | 🔴 |

## Oven (`OV`)

Asked for: observations and the stop/off codes only.

| Code | Should do | Level |
|---|---|---|
| `OVGENMO00000` | Off | 🟢 |
| `OVGENMO00003` | Stop (send it while the oven is idle or cooling; does nothing harmful) | 🟢 |

Known from the app, **not requested**: `OVGENMO` 1 = config, 2 = start, 8 = continue; `OVPROSE` program (0 defrost, 1 turbo, 2 conventional,
3 fan assisted, 4 pizza, 6 full grill, 7 grill + fan, 12 bottom, 15 3D, 16 steam clean); `OVTEMSE` target °C (50 … 275, step 5);
`OVDFREM` duration in minutes; `OVBSTSE` boost 0 / 1. If you have seen what the app sends for these (a screenshot of the
app's own log, for instance), that helps more than sending them.

## Air conditioner extras (models that have these features)

The basics (mode, fan, temperature, louvers, timers) are already verified. The sample capability files also list the
following. Try them only if the app shows the feature on your unit.

| Code | Should do | Level |
|---|---|---|
| `ACUVSET00001` / `ACUVSET00000` | UV-C sterilisation on / off | 🟢 |
| `ACRGBON00001` / `ACRGBON00000` | Indicator light on / off | 🟢 |
| `ACRGBST00000` … `00003` | Light colour tone 1 … 4 | 🟢 |
| `ACRGBBR00001` … `00003` | Light brightness low / medium / high | 🟢 |
| `ACQOFFT00961` | Quick-off timer: 1 h 30 min (hour + minute × 32) | 🟡 |
| `ACQOFFT02047` | Cancel the quick-off timer | 🟡 |
| `ACSAFRS00001` | Reset the odour and allergen filter life counter. Only after you really cleaned or replaced it | 🟡 |
| `ACSAFRS00010` | Reset the particle sensor cleaning counter. Same rule | 🟡 |

## Reporting

[Open an issue](https://github.com/mutlutekir/Vestel_Smart_Life/issues/new?template=device-test-report.yml)
and fill in the form. In short: appliance type and model, integration version, the code you sent, what the
appliance and the app did, and the **before** and **after** raw status. Do not post your password or token.
Remove anything you consider private.

---

<a id="türkçe"></a>

# 🇹🇷 Türkçe

Gerçek cihazda yalnızca klimalar doğrulandı. Buzdolabı için kontrol varlıkları var; diğer cihazlar
(çamaşır makinesi, kurutmalı çamaşır makinesi, kurutma makinesi, bulaşık makinesi, fırın, buzdolabı-dondurucu)
salt okunur. Hepsi Smart Life uygulamasından çıkarıldı, **cihazlarda denenmedi**.

Bu cihazlardan birine sahipsen yardımcı olabilirsin: aşağıdaki kodları `vestel_smart_life.send_raw_code`
servisiyle gönder, cihazın ne yaptığına bak ve sonucu
[issue açarak](https://github.com/mutlutekir/Vestel_Smart_Life/issues/new?template=device-test-report.yml) bildir.
"`WMUISET01283` → ekranda 40 °C / 1000 devir göründü" gibi tek satır bile işe yarar. "Hiçbir şey olmadı" da değerli bir sonuçtur.

## Önce güvenlik

- **Gönderdiğin koddan sen sorumlusun.** Bu kodlar resmi uygulamanın gönderdikleri, ama entegrasyon bunları senin modeline hiç göndermedi.
- Yalnızca başında durabileceğin şeyleri dene. Çamaşır, kurutma ve bulaşık makinesinde: **makine boş, sen odadasın, su ve gider bağlı.** Elin cihazın durdur tuşuna yakın olsun.
- Her kodun bir seviyesi var:
  - 🟢 zararsız: bir anahtar ya da ekran ayarı, hiçbir şey başlamaz.
  - 🟡 bir ayarı değiştirir (program, sıcaklık, mod, erteleme). Hiçbir şey başlamaz. Sonra eski değere geri al.
  - 🔴 programı başlatır, duraklatır ya da durdurur. Yalnızca başında durarak ve boş makinede.
- **Fırın:** lütfen başlatma ya da ısıtma komutu gönderme. Yalnızca gözlemler ve 🟢 durdur/kapat kodları isteniyor. Diğer fırın kodları, raporlar bunlara atıfta bulunabilsin diye listelendi.
- **Buzdolabı:** bir bölmeyi kapatma, testten sonra sıcaklığı eski haline getir; yiyecekler bozulmasın.
- Tablolarda olmayan değerler gönderme. Bunları kimse denemedi; yanlış değer cihazı fişi çekmeden düzelmeyen bir duruma sokabilir.

## Nasıl denenir

1. **Geliştirici araçları → Eylemler** bölümünde `vestel_smart_life.dump_raw_status`
   eylemini seç (listede "Ham durumu göster (debug)" adıyla durur), cihazı seç, çalıştır. Bildirimde tüm kayıtlar görünür.
   Kopyala: bu **önceki** durum.
2. Bir kod gönder:

   ```yaml
   action: vestel_smart_life.send_raw_code
   data:
     device_id: <arayüzden cihazı seç>
     code: "RFCLOCK00001"
   ```

   Kod, 7 harfli kayıt adı ve ardından 5 haneli sayıdır, boşluk yok.
3. Yaklaşık 10 saniye bekle (bulut yavaş olabilir), sonra `dump_raw_status` eylemini tekrar çalıştır. Bu **sonraki** durum.
   Bunun için varlıklara güvenme: klima dışındaki cihazlar 30 saniyede bir yenilenir.
4. Cihaza ve Smart Life uygulamasına bak. Ekran değişti mi? Uygulama da değişikliği gösterdi mi?
5. Eski değeri geri yaz, sonra sıradaki koda geç. Her seferinde tek kod.

## Gözlemler (komut gerekmez)

En çok işe yarayan ve hiçbir riski olmayan kısım. Her durumda `dump_raw_status` çalıştır ve değişen kayıtları not et.

| Cihaz | Ne yapılır | Ne öğreniriz |
|---|---|---|
| Buzdolabı | **Yalnızca soğutucu kapağını** aç, ham durumu al. Kapat. **Yalnızca dondurucu kapağını** aç, al. İkisini birden aç, al. | `RFDOORA` değerlerinin 0, 1 ve 2 için anlamı (örnek belge ile bir rapor çelişiyor). |
| Buzdolabı | Cihaz ekranında bilinen bir sıcaklık varken `RFTEMSE` değerini oku. | Soğutucu ve dondurucu değerlerinin doğruluğu. |
| Buzdolabı-dondurucu | Sıcaklık kayıtlarını (adı `TE` ile biten) cihaz ekranıyla karşılaştır. | Kodlamaları (işaretli sayı tahmin ediyoruz). |
| Çamaşır, kurutmalı çamaşır, kurutma, bulaşık makinesi | Boşta, program seçili, çalışıyor, duraklatılmış, kapak açık, bitti. Her birinde al. | Durum, adım ve hata kayıtları. |
| Çamaşır, kurutma, bulaşık makinesi | Uygulamadan örneğin 3 saat erteleme ayarla, sonra al. | Erteleme kayıtlarının dakika mı saat mi olduğu. |
| Hepsi | Cihaz kendiliğinden bir arıza gösterirse, görünürken al. | Hangi hata biti ya da kodu neyi gösteriyor. |

## Buzdolabı (`RF`)

Entegrasyonda bunlar için zaten varlıklar var (çocuk kilidi, ekran koruyucu, mod, sıcaklıklar). Önce varlıkları dene;
ham kodlar karşılaştırma ve varlığı olmayan kayıtlar için.

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `RFCLOCK00001` / `RFCLOCK00000` | Çocuk kilidi açık / kapalı | 🟢 |
| `RFSSAVE00001` / `RFSSAVE00000` | Ekran koruyucu açık / kapalı | 🟢 |
| `RFMODEA00000` | Normal mod | 🟡 |
| `RFMODEA00002` | Süper dondurma | 🟡 |
| `RFMODEA00004` | Süper soğutma | 🟡 |
| `RFMODEA00008` | Tatil | 🟡 |
| `RFMODEA00016` | Ekonomi (örnekte yok, modele bağlı olabilir) | 🟡 |
| `RFMODEA00032` | Yapay zeka | 🟡 |
| `RFTEMSE01042` | Soğutucu 4 °C, dondurucu −18 °C | 🟡 |
| `RFTEMSE00536` | Soğutucu 2 °C, dondurucu −24 °C | 🟡 |
| `RFTEMSE02064` | Soğutucu 8 °C, dondurucu −16 °C | 🟡 |
| `RFDCOOL00001` | Hızlı içecek soğutma (örnekte durumlar: 0 açık, 1 kapalı, 2 bitti). Bu kaydın yazılabilir olup olmadığını bilmiyoruz. | 🟡 |

`RFTEMSE` = soğutucu × 256 + dondurucu (dondurucu eksi işaretsiz). Soğutucu: 2, 4, 5, 6, 8. Dondurucu: 16, 18, 20, 22, 24.
Aynı anda yalnızca bir mod etkin olur.

## Buzdolabı-dondurucu (`FD`)

Her ayar tek sayı tutan bir kayıt. Hangi bölmenin hangisi olduğu modele göre değişir: listesi 1–8 olan bölme soğutucu,
diğeri dondurucu. `00000` (kapalı) değerini asla gönderme.

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `FDMAINA00001` … `FDMAINA00008` | Ana bölme 1 … 8 °C | 🟡 |
| `FDMAINA00009` | Süper soğutma | 🟡 |
| `FDZONE1` / `FDZONE2` için 1 … 8 | Soğutucu bölme 1 … 8 °C (`FDZONE1` 9 = olan modellerde VitaStore) | 🟡 |
| `FDZONE1` için 10 … 20 | Dondurucu bölme −14 … −24 °C (10 = −14, 11 = −15, …, 20 = −24); 21 = süper dondurma | 🟡 |
| `FDZONE2` için 9 … 19 | Dondurucu bölme −14 … −24 °C (9 = −14, 10 = −15, …, 19 = −24); 20 = süper dondurma | 🟡 |
| `FDMODE2` için 0 / 1 / 2 | Mod yok / Ekonomi / Tatil | 🟡 |

Örnek: bölme 2'nin dondurucu olduğu bir modelde `FDZONE200013` = −18 °C. Raporda iki bölmeden hangisinin değiştiğini yaz.

## Çamaşır makinesi (`WM`)

Tambur boş, kapak kapalı, başında duruyorsun. Program numaraları modele göre değişir: uygulamanın gösterdiği listeyi
tabloyla karşılaştır (örnek model T225).

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `WMFORPR00003` | Pamuklu programını seç | 🟡 |
| `WMFORPR00019` / `00002` / `00005` / `00004` / `00007` / `00008` | Eko 40-60 / Ön yıkamalı pamuklu / Pamuklu 20 / Renkliler / Yünlü / Durulama | 🟡 |
| `WMFORPR00016` / `00009` / `00010` / `00006` / `00012` / `00013` / `00014` / `00015` | Alerji / Sıkma+boşaltma / El yıkama gömlek / Kolay bakım outdoor / Yorgan / Perde / Hızlı 60 / Hızlı 15 | 🟡 |
| `WMUISET01283` | Sıcaklık 40 °C, devir 1000 | 🟡 |
| `WMUISET01026` | 30 °C ve 800 devir | 🟡 |
| `WMUISET00000` | Soğuk ve sıkma yok | 🟡 |
| `WMUISO1<n>` | Seçenek bitleri: 2 = hızlı yıkama, 1024 = karışık. Bit alanı: önce ham durumdaki mevcut değeri oku ve toplamı gönder, yoksa diğer seçenekler kapanır. | 🟡 |
| `WMDELAY00060` | 60'lık erteleme (dakika mı saat mi? ekranda ne gördüğünü yaz) | 🟡 |
| `WMDCPST00002` | Ayarlanan erteleme ile başlat | 🔴 |
| `WMDCPST00001` | Başlat | 🔴 |
| `WMDCPST00003` | Duraklat | 🔴 |

`WMUISET` = sıcaklık kodu + devir kodu × 256. Sıcaklık: 0 soğuk, 1 = 20, 2 = 30, 3 = 40, 4 = 50, 5 = 60, 6 = 70, 7 = 80, 8 = 90 °C.
Devir: 0 yok, 1 = 400, 3 = 600, 4 = 800, 5 = 1000, 6 = 1200.
`WMCANCL` (iptal) uygulamada var ama değeri bilinmiyor; bir kayıtta görürsen bildir.

## Kurutmalı çamaşır makinesi (`WD`)

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `WDFORPR00019` | Eko 40-60 seç | 🟡 |
| `WDFORPR00002` / `00004` / `00005` / `00006` / `00007` / `00008` | Pamuklu / Pamuklu 20 / Sentetik / Yün-ipek / Yorgan / Durulama | 🟡 |
| `WDFORPR00012` / `00009` / `00011` / `00010` | Alerji / Sıkma+boşaltma / Hızlı 15 / Hızlı 60 | 🟡 |
| `WDFORPR00013` / `00014` / `00015` / `00016` | Hassas kurutma / Pamuklu kurutma / Jet yıkama kurutma / 6 saat yıkama sonrası pamuklu kurutma | 🟡 |
| `WDUISET<n>` | Sıcaklık + devir × 256, çamaşır makinesi gibi. Devir: 0 yok, 1 = 400, 4 = 800, 5 = 1000, 6 = 1200, 7 = 1400. Sıcaklık: 0 soğuk, 1 = 20, 2 = 30, 3 = 40, 5 = 60, 6 = 70, 7 = 80, 8 = 90. | 🟡 |
| `WDDRYOP00514` | Kurutma seviyesi 2 ve 60 dakika (seviye + süre × 256; seviye 0-3, süre 0 yok, 1 = 30, 2 = 60, 3 = 90, 4 = 120 dk) | 🟡 |
| `WDUISO1<n>` | Seçenek bitleri: 4 ön yıkama, 8 kolay ütü, 16 ekstra durulama, 32 alerji önleyici (bit alanı, yukarıya bak) | 🟡 |
| `WDECOSP<n>` | Bitler: 1 tasarruf plus, 2 hız | 🟡 |
| `WDDELAY00060` | 60'lık erteleme (birim?) | 🟡 |
| `WDDCPST00001` / `00002` / `00003` | Başlat / erteleyerek başlat / duraklat | 🔴 |

## Bulaşık makinesi (`DW`)

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `DWPROSI00004` | Eko 50 seç | 🟡 |
| `DWPROSI00002` / `00003` / `00005` / `00006` / `00007` / `00008` / `00010` / `00017` / `00023` | Jetwash 14 / Hızlı 30 / Dual pro / Süper 50 / Akıllı 30-50 / Akıllı 50-60 / Buharlı / Tasarruf 54 / Kristal ışık | 🟡 |
| `DWPROSI00000` | Sıfırla | 🟡 |
| `DWFAVSS00001` | Favori 1'i seç | 🟡 |
| `DWPROOP<n>` | Seçenekler, her biri bir bit: 2 tablet, 8 üst püskürtme, 16 alt püskürtme, 32 ekstra hızlı, 64 ekstra sessiz, 128 otomatik kapak, 512 ekstra kurutma, 1024 ekstra hijyen. Toplamı gönder, örneğin `DWPROOP00520` = ekstra kurutma (512) + üst püskürtme (8). | 🟡 |
| `DWDFDEL00060` | Erteleme (örnekte dakika, adım 60) | 🟡 |
| `DWPROST00001` | Başlat (çalışıyor) | 🔴 |
| `DWPROST00002` | Duraklat | 🔴 |
| `DWPROST00000` | Program öncesi duruma dön | 🔴 |

Not: seçenekler program öncesi durumda seçilmeli ve her programda yalnızca bazıları geçerli. Önce mevcut `DWPROOP` değerini
oku ve tek bit değiştir.

## Kurutma makinesi (`TD`)

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `TDCHLOC00001` / `TDCHLOC00000` | Çocuk kilidi açık / kapalı | 🟢 |
| `TDBUZZR00001` / `TDBUZZR00000` | Sesli uyarı açık / kapalı | 🟢 |
| `TDSELPR00001` | Pamuklu ekstra kuru seç (değer + bilmediğimiz 2 bitlik alan; 0 bırak) | 🟡 |
| `TDSELPR00002` … | 2 dolap kuru, 3 ütü kuru, 4 sentetik dolap, 5 sentetik ütü, 6 hassas, 7 karışık, 8 bebek bakımı, 14 tazeleme, 16 ekspres, 19 gömlek, 21 süreli kurutma, 22 yorgan, 23 spor, 24 yün tazeleme | 🟡 |
| `TDDRYLV00002` | Kurutma seviyesi 2 (0-3) | 🟡 |
| `TDOPANT00001` / `00000` | Buruşma önleme (60 dk) açık / kapalı | 🟡 |
| `TDOPDEL00001` | Hassas seçeneği | 🟡 |
| `TDOPION00001`, `TDOPUVC00001` | İyon / UV seçeneği (yalnızca olan modellerde) | 🟡 |
| `TDTIDRY00060` | Süreli kurutma 60 dk (20, 30, 40, 50, 60, 80 … 200); tazeleme programında 10 … 120 | 🟡 |
| `TDDTIMR00060` | Erteleme (0 … 1380, adım 60) | 🟡 |
| `TDSTART00001` | Başlat. Uygulama kodu 1 gönderiyor, örnek belge 2 diyor | 🔴 |
| `TDSTART00002` | 1 bir şey yapmadıysa başlat. Hangisinin çalıştığını bildir | 🔴 |

## Fırın (`OV`)

İstenenler: yalnızca gözlemler ve durdur/kapat kodları.

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `OVGENMO00000` | Kapalı | 🟢 |
| `OVGENMO00003` | Durdur (fırın boştayken ya da soğurken gönder; zararı yok) | 🟢 |

Uygulamadan bilinen ama **istenmeyenler**: `OVGENMO` 1 = ayar, 2 = başlat, 8 = devam; `OVPROSE` program (0 çözme, 1 turbo, 2 statik,
3 fanlı, 4 pizza, 6 tam ızgara, 7 ızgara + fan, 12 alt, 15 3D, 16 buharlı temizlik); `OVTEMSE` hedef °C (50 … 275, adım 5);
`OVDFREM` süre (dakika); `OVBSTSE` boost 0 / 1. Uygulamanın bunlar için ne gönderdiğini gördüysen (örneğin uygulamanın kendi
kaydından bir ekran görüntüsü), göndermekten daha çok işe yarar.

## Klima ekstraları (bu özellikleri olan modeller)

Temel kontroller (mod, fan, sıcaklık, kanatçıklar, zamanlayıcılar) zaten doğrulandı. Örnek yetenek dosyaları şunları da listeliyor.
Yalnızca uygulama bu özelliği cihazında gösteriyorsa dene.

| Kod | Ne yapmalı | Seviye |
|---|---|---|
| `ACUVSET00001` / `ACUVSET00000` | UV-C sterilizasyon açık / kapalı | 🟢 |
| `ACRGBON00001` / `ACRGBON00000` | Gösterge ışığı açık / kapalı | 🟢 |
| `ACRGBST00000` … `00003` | Işık rengi tonu 1 … 4 | 🟢 |
| `ACRGBBR00001` … `00003` | Işık parlaklığı düşük / orta / yüksek | 🟢 |
| `ACQOFFT00961` | Hızlı kapatma zamanlayıcısı: 1 sa 30 dk (saat + dakika × 32) | 🟡 |
| `ACQOFFT02047` | Hızlı kapatmayı iptal et | 🟡 |
| `ACSAFRS00001` | Koku ve alerjen filtre ömrü sayacını sıfırla. Yalnızca gerçekten temizlediysen ya da değiştirdiysen | 🟡 |
| `ACSAFRS00010` | Parçacık sensörü temizlik sayacını sıfırla. Aynı kural | 🟡 |

## Bildirme

[Issue aç](https://github.com/mutlutekir/Vestel_Smart_Life/issues/new?template=device-test-report.yml)
ve formu doldur. Kısaca: cihaz türü ve modeli, entegrasyon sürümü, gönderdiğin kod, cihazın ve uygulamanın ne yaptığı ve
**önceki** ile **sonraki** ham durum. Şifreni ya da token'ını paylaşma. Özel saydığın her şeyi silebilirsin.
