# Sürüm Notları

## v0.0.3 — Mükellef menfaati ve zorunlu iç bildirim

- Her vakada en az bir hukuka uygun ve güncel mükellef lehine adımı zorunlu yapan `taxpayer_interest_engine.py` eklendi.
- Aleyhe her husus için kullanıcı/SMMM/YMM alıcılı, görülme tarihli ve otomatik dış iletime kapalı yerel iç bildirim zorunlu oldu.
- Aleyhe olgu/kanıt gizleme, hukuka aykırı yöntem, tarafsızlık/bağımsızlık kaybı ve insan incelemesini kaldırma fail-closed `BLOCK` kurallarına bağlandı.
- 5 kaynak kaydı, 16 sürümlü kural ve sabit katalog SHA-256 özeti içeren `taxpayer_interest_rules.v1.json` eklendi.
- Lehe adım ve iç bildirimler fiziksel UTF-8 JSON dosyası, eşleşen kimlik ve SHA-256 özetiyle vaka kapanışına bağlandı.
- Mükellef menfaati kapısı `case.json` ile kapatılamayan bütün-vaka kuralı oldu.
- `$muhasebecim`, `$vergi-mufettisi` ve `$yeminli-mali-musavir` tek merkezî politika dosyasına bağlandı.
- Vergi müfettişi modunda lehe/aleyhe kanıtın birlikte değerlendirilmesi; YMM modunda bağımsızlık ve doğru raporlamanın korunması açıkça kilitlendi.
- Mali müşavir için ayrıntılı politika, kullanım ve yazılımı çalıştırmadan kurgusal vaka üzerinden öğrenme rehberleri eklendi.
- Otomatik test paketi 72 teste çıkarıldı.
- Test sayısı, dosya bazlı dağılımı, pozitif/negatif yöntemleri, kurcalama/hash ve entegrasyon kontrolleri ayrı metodoloji belgesi ile makinece okunabilir test sonuç kaydında yayımlandı.
- Projenin başlangıç talepleri, hedef mimarisi, tamamlanan çıktıları, açık eksikleri, güncel çalışma durumu ve gerçek veri yol haritası ayrıntılı durum belgesinde yayımlandı.

## v0.0.2 — Vergi müfettişi ve YMM uzmanlıkları

- Vergi incelemesi hazırlığı ve yetkili müfettiş desteği modları eklendi.
- YMM tasdik öncesi hazırlık ve ruhsatlı YMM desteği modları eklendi.
- 17 mevzuat kaynağına bağlı 48 deterministic rol kuralı eklendi.
- Yetki, ruhsat, bağımsızlık, sözleşme, kanıt, karşıt inceleme ve rapor kalite kapıları vaka akışına bağlandı.
- Codex eklenti manifesti ve üç uzmanlık becerisi yayımlandı.

## v0.0.1 — İlk public pilot

- Yerel belge/mevzuat ingest sistemi,
- Python hesaplama çekirdeği,
- vaka tamamlama döngüsü,
- sürümlü THP kataloğu,
- deterministik THP/VUK hesap, yevmiye ve mizan kontrolleri,
- mali müşavir kullanım rehberi

ilk public pilot olarak yayımlandı.
