# Mali Müşavirim (`muhasebecim`)

Türk muhasebesi ve mali müşavirlik işleri için yerel veri işleyen, resmî kaynak sürümleyen ve bütün sayısal işlemleri denetlenebilir Python koduyla yapan Codex yeteneği.

**Güncel sürüm:** `v0.0.3`

**İlk public pilot sürüm:** `v0.0.1`

Sürüm bazında eklenen özellikler için [Sürüm Notları](CHANGELOG.md) dosyasına bakın.

**Doğrulanmış test durumu:** `72/72 PASS` — başarısız `0`, hata `0`, atlanan `0`. Test kapsamı, pozitif/negatif yöntemler ve güvence sınırları için [Test Yöntemi ve Doğrulama Sonuçları](docs/TEST-YONTEMI-VE-SONUCLARI.md); makinece okunabilir kayıt için [v0.0.3 test sonucu](docs/test-results-v0.0.3.json) dosyasına bakın.

## Ne istedik, neyi hedefledik, neyi başardık, şimdi ne yapıyoruz?

Bu proje; Türk muhasebe ve vergi uygulamalarını yerelde inceleyen, bütün sayısal işlemleri Python ile yapan, THP/VUK kurallarını deterministik kapılarla uygulayan ve işi meslek mensubu incelemesine hazırlayan bir sanal mali müşavir sistemi kurma talebiyle başladı.

Hedefimiz tek seferlik cevap üreten bir sohbet değil; belge kabulünden resmî kaynağa, Python hesabından THP/VUK kontrolüne, mükellef lehine adımdan aleyhe yerel iç bildirime ve fiziksel SHA-256 kanıtına kadar uçtan uca çalışan bir dosya metodolojisidir.

Bugün itibarıyla yerel ingest, 14 hesap işlemi, 271 hesaplı genel THP kataloğu, 48 profesyonel rol kuralı, 16 mükellef menfaati kuralı, üç uzmanlık becerisi, zorunlu vaka kapıları, meslek rehberleri ve 72 başarılı test tamamlandı.

Henüz gerçek müşteri verisi pilotu, bütün vergi mevzuatının kurallaştırılması, tüm TMS/TFRS paragrafları, sektörel hesap planları, canlı GİB/e-Defter entegrasyonu ve bağımsız güvenlik/performans denetimi tamamlanmadı. Şimdiki hedef, kullanıcının sağlayacağı gerçek muhasebe kayıtlarını yerelde çalıştırmak ve sistemin gerçek veri üzerindeki yanlış pozitiflerini, veri eşlemelerini ve eksik kurallarını ölçmektir.

İsteklerin kronolojisi, hedef mimari, tamamlanan işler, açık eksikler, güncel çalışma ve yol haritası için [Proje Amacı, Kapsamı ve Güncel Durumu](docs/PROJE-AMACI-KAPSAMI-VE-DURUMU.md) belgesini okuyun.

Mali müşavir açısından sistemin ne yaptığını, hangi verinin nasıl hazırlanacağını, THP/VUK bulgularının nasıl okunacağını ve gerçek veri testinin nasıl yürütüleceğini öğrenmek için [Mali Müşavir Kullanım Rehberi](docs/MALI-MUSAVIR-KULLANIM-REHBERI.md) ile başlayın.

Yazılımı hiç çalıştırmadan bütün sistemi kurgusal bir muhasebe vakası üzerinden kavramak için [Mali Müşavirim'i Yazılımı Çalıştırmadan Anlama Rehberi](docs/SISTEMI-KULLANMADAN-ANLAMA-REHBERI.md) dosyasını okuyun. Bu rehber; belge kabulünden THP/VUK kontrolüne, Python hesap izinden mükellef lehine adıma, aleyhe iç bildirimden vergi müfettişi/YMM bakışına kadar tüm zinciri mali müşavir diliyle örnekler.

Vergi müfettişi bakışı, vergi incelemesi hazırlığı ve YMM tasdik kapıları için [Vergi Müfettişi ve YMM Uygulama Rehberi](docs/VERGI-MUFETTISI-YMM-REHBERI.md) dosyasını okuyun.

Her vakada hukuka uygun mükellef lehine adım hazırlanması ve aleyhe hususların zorunlu yerel iç bildirimi için [Mükellef Menfaati ve İç Bildirim Rehberi](docs/MUKELLEF-MENFAATI-VE-IC-BILDIRIM.md) dosyasını okuyun.

## Mali müşavir için kısa açıklama

Bu sistem bir muhasebe programı veya beyanname gönderim aracı değildir. Mizan, yevmiye, hesap listesi ve hesaplama girdilerini yerelde kontrol eden ikinci göz niteliğindedir. Katalogda olmayan hesap, hesap adı uyuşmazlığı, 7/A-7/B karışması, dengesiz fiş, mizan devir hatası, VUK kayıt süresi ve tevsik eksikliği gibi tanımlı durumları kural kimliğiyle raporlar.

Sonuçtaki `PASS`, yalnız tanımlı mekanik kontrollerin geçtiğini gösterir. Belgenin gerçekliği, hesabın ekonomik öz bakımından nihai doğruluğu, beyanname uygunluğu ve mesleki imza sorumluluğu ruhsatlı meslek mensubunda kalır.

## Teslim edilen sistem

- SMMM çalışma modeli: iş kabulü ve sözleşmeden belge akışı, kayıt, aylık kapanış, beyan, dönem sonu, raporlama ve devre kadar kontrol kapıları.
- TMS/TFRS, BOBİ FRS, KÜMİ FRS, VUK ve Tekdüzen/MSUGT için konu yönlendiricileri ve yürürlük politikası.
- Açık resmî kaynakları yerel korpusa alan, SHA-256 ile sürümleyen, metin çıkaran ve arayan ingest sistemi.
- Müşteri verisini cihaz dışına çıkarmayan yerel-only analiz politikası.
- `Decimal` tabanlı 14 işlemli hesap motoru: yevmiye denkliği, amortisman, bugünkü değer, etkin faiz, stok, kur, endeksleme, değer düşüklüğü, ertelenmiş vergi, ticari-mali kâr, KDV ve gün hesabı.
- Vaka klasörü açan ve işi “meslek mensubu incelemesine hazır” olana kadar deterministik çıkış kapılarıyla kontrol eden çalışma döngüsü.
- Otomatik testler ve 2 Ağustos 2026 tarihinde yeniden doğrulanmış, sürüm izli resmî kaynak korpusu.
- CSV/TSV/JSON/TXT, metin katmanlı PDF ve XLSX/XLSM müşteri kayıtlarını tamamen yerelde alan vaka ingest'i; elektronik tablo formülleri ve makroları çalıştırılmaz.
- Sürümlü genel THP kataloğu üzerinde 271 tanımlı hesap, iki proje hesabı aralığı ve 10 kaynak kaydıyla çalışan deterministik THP/VUK kural motoru.
- VUK 5 ve 134-142/256/359/367 ile VDK usullerini iş akışına dönüştüren `$vergi-mufettisi` yeteneği.
- 3568 sayılı Kanun ve YMM yönetmeliklerinden türetilen bağımsızlık, sözleşme, kanıt, karşıt inceleme ve rapor kapılarına sahip `$yeminli-mali-musavir` yeteneği.
- 17 mevzuat kaynağına bağlı 48 kuralla çalışan `professional_role_engine.py`; yetki/ruhsat eksikliğinde fail-closed, aynı girdide aynı SHA-256 makbuzu.
- 5 kaynak kaydına bağlı 16 kapalı kuralla çalışan `taxpayer_interest_engine.py`; her vakada güncel hukuka uygun lehe adım, aleyhe hususta yerel iç bildirim, kullanıcı/SMMM/YMM görülme kaydı ve insan onayı.
- Lehe adım ve iç bildirim dosyasını yalnız “hazır” beyanıyla kabul etmeyen fiziksel dosya + SHA-256 vaka kapısı; `case.json` ile kapatılamaz.
- Codex eklenti manifesti: tek kurulumda muhasebe, vergi incelemesi ve YMM tasdik uzmanlıkları.

## Codex eklentisi ve uzmanlıklar

Depo kökündeki `.codex-plugin/plugin.json`, `skills/` altındaki üç yeteneği tek eklenti olarak kaydeder:

- `$muhasebecim`: genel muhasebe, THP/VUK, raporlama çerçeveleri ve Python hesapları,
- `$vergi-mufettisi`: vergi incelemesi hazırlığı, hak/yükümlülük ve kanıt dosyası,
- `$yeminli-mali-musavir`: YMM tasdik kabulü, bağımsızlık, denetim ve rapor kalite kapıları.

Rol motoru kamu yetkisi, ruhsat, imza veya mühür üretmez. Her sonuçta `professional_act_permitted` alanı `false` kalır.

Üç yetenek tek [mükellef menfaati politikasına](skills/muhasebecim/references/taxpayer-interest-policy.md) tabidir: dış taslakta mükellefi gereksiz zayıflatan ikrar/ifade üretilmez; aleyhe olgu ise yerel iç analizde asla saklanmaz. Bu ayrım doğru kayıt, zorunlu beyan, YMM bağımsızlığı veya vergi müfettişi tarafsızlığını kaldırmaz.

## Deterministik THP/VUK motoru

Motorun tasarımında [bcancapar-spec/ortak-avukat](https://github.com/bcancapar-spec/ortak-avukat) projesindeki deterministik kapı, açık kural kimliği, makinece okunabilir kanıt ve fail-closed çıktı yaklaşımından ilham alındı. Uygulama muhasebe alanı için sıfırdan yazıldı; diğer deponun kaynak kodu kopyalanmadı.

`thp_rule_engine.py` dört işlem sağlar:

- `catalog-audit`: kurulu katalog yapısını, kaynak bağlarını ve tekrarları denetler.
- `account-validate`: hesap kodu/adı, yürürlük, sektör ve 7/A-7/B politikasını kontrol eder.
- `journal-validate`: THP kontrollerine VUK 215, 217, 218, 219 ve 227 kayıt kapılarını ve yevmiye denkliğini ekler.
- `trial-balance-validate`: hesap, normal bakiye, açılış-hareket-kapanış devri ve mizan toplamlarını doğrular.

Aynı girdi ve aynı katalog kanonik olarak aynı JSON sonucu verir. Sonuçta girdi/katalog SHA-256 özetleri, sıralı bulgular, kaynak referansları ve kurcalamayı fark ettiren `receipt_sha256` bulunur. Çıkış kodu `0` geçiş, `1` iş kuralı bloku, `2` kapalı şema veya sistem hatasıdır.

Katalog genel MSUGT planıyla sınırlıdır. Banka, sigorta, katılım finans, finansal kiralama, faktoring ve sermaye piyasası işletmelerinde genel plan otomatik uygulanmaz. Kod uygunluğu işlemin ekonomik sınıflandırmasının, belgenin gerçekliğinin veya beyannamenin doğruluğunun kanıtı değildir.

## Yerel veri garantisi

Kodlama dili Python 3.11+'dır. Müşteri belgesi, mizan, bordro, banka hareketi ve diğer vaka verileri uzak OCR, embedding, LLM veya analiz hizmetine gönderilmez. Ağ yalnızca manifestteki açık resmî kaynakları indirmek için kullanılır; çıkarım, indeksleme, arama ve hesaplama yerelde yapılır.

`cases/`, `corpus/` ve yaygın muhasebe veri dosyaları `.gitignore` ile GitHub dışında tutulur. Gerçek müşteri kayıtlarını hiçbir zaman kaynak kod deposuna eklemeyin.

## Hızlı kullanım

Testleri çalıştır:

```powershell
python -m unittest discover -s .\skills\muhasebecim\scripts -p "test_*.py" -v
```

Test sayısını ve sonucu makinece okunabilir JSON olarak yeniden üret:

```powershell
python .\skills\muhasebecim\scripts\test_suite_report.py
```

Test yöntemi; pozitif geçiş, negatif/fail-closed blok, kapalı şema, deterministik tekrar, katalog kurcalama, sonuç makbuzu, fiziksel dosya/SHA-256, CLI çıkış kodları ve uçtan uca vaka kapanışı kontrollerini birlikte kullanır.

Resmî korpusu yenile ve denetle:

```powershell
python .\skills\muhasebecim\scripts\ingest_sources.py ingest `
  --manifest .\manifests\official-sources.json `
  --corpus .\corpus\official

python .\skills\muhasebecim\scripts\ingest_sources.py audit `
  --corpus .\corpus\official
```

Yalnız THP/VUK kural motoru dayanaklarını yenilemek için hedefli manifesti kullan:

```powershell
python .\skills\muhasebecim\scripts\ingest_sources.py ingest `
  --manifest .\manifests\thp-vuk-sources.json `
  --corpus .\corpus\official
```

Vergi incelemesi ve YMM tasdik dayanaklarını yerel korpusa al:

```powershell
python .\skills\muhasebecim\scripts\ingest_sources.py ingest `
  --manifest .\manifests\professional-roles-sources.json `
  --corpus .\corpus\official
```

Yerel korpusta ara:

```powershell
python .\skills\muhasebecim\scripts\query_corpus.py `
  --corpus .\corpus\official `
  --query "amortisman"
```

2026 Mavi Kitap'tan vakaya ilişkin tam standart metinlerini seçerek ingest et:

```powershell
python .\skills\muhasebecim\scripts\prepare_2026_tfrs_manifest.py `
  --standards TMS-2 TMS-16 TFRS-15 --as-of 2026-08-02 `
  --output .\manifests\selected-tfrs.json
```

Yeni vaka aç ve tamamlanma kapılarını çalıştır:

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py init `
  --case .\cases\ornek-vaka --case-id ornek-vaka --as-of 2026-08-02

python .\skills\muhasebecim\scripts\case_workflow.py check `
  --case .\cases\ornek-vaka

python .\skills\muhasebecim\scripts\case_workflow.py finalize `
  --case .\cases\ornek-vaka
```

Hesap işlemlerini gör ve birini çalıştır:

```powershell
python .\skills\muhasebecim\scripts\muhasebecim_engine.py --list
python .\skills\muhasebecim\scripts\muhasebecim_engine.py vat --example
python .\skills\muhasebecim\scripts\muhasebecim_engine.py vat `
  --input .\case.json --output .\result.json
```

THP/VUK kataloğunu ve kayıtları doğrula:

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py catalog-audit
python .\skills\muhasebecim\scripts\thp_rule_engine.py journal-validate --example `
  --output .\journal-example.json
python .\skills\muhasebecim\scripts\thp_rule_engine.py journal-validate `
  --input .\journal-example.json --output .\journal-result.json
```

Gerçek vaka kapısında `case.json` içindeki `requires_thp_validation` alanını `true` yap ve sonucu `outputs/thp-validation-result.json` olarak üret. Tam girdi sözleşmesi ve kural haritası [thp-control.md](skills/muhasebecim/references/thp-control.md) dosyasındadır.

Vergi incelemesi ve YMM tasdik kapılarını çalıştır:

```powershell
python .\skills\muhasebecim\scripts\professional_role_engine.py catalog-audit
python .\skills\muhasebecim\scripts\professional_role_engine.py `
  inspection-readiness-validate --example --output .\inspection-readiness.json
python .\skills\muhasebecim\scripts\professional_role_engine.py `
  ymm-certification-validate --example --output .\ymm-certification.json
```

Vaka kapısında ilgili `requires_inspection_readiness` veya `requires_ymm_certification` alanını `true` yapın. Motor sonuçlarını sırasıyla `outputs/inspection-readiness-result.json` ve `outputs/ymm-certification-result.json` yollarına yazın.

Mükellef menfaati ve iç bildirim kapısını çalıştır:

```powershell
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py catalog-audit
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py `
  taxpayer-interest-validate --example --output .\taxpayer-interest.json
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py `
  taxpayer-interest-validate --input .\taxpayer-interest.json `
  --output .\cases\ornek-vaka\outputs\taxpayer-interest-result.json
```

Bu sonuç tüm vakalarda zorunludur. `case_workflow.py`, aktif lehe adım ile aleyhe iç bildirimlerin vaka içindeki fiziksel dosyalarını ve SHA-256 özetlerini de doğrular.

## Yapı

```text
muhasebecim/
├── .codex-plugin/plugin.json         # Üç yeteneği kaydeden eklenti manifesti
├── docs/                            # Mali müşavir, uzmanlık ve mükellef menfaati rehberleri
├── corpus/official/                 # Yerel, hash denetimli başlangıç korpusu
├── manifests/                       # Genel ve hedefli resmî kaynak manifestleri
└── skills/
    ├── muhasebecim/                 # Muhasebe, THP/VUK ve ortak Python motorları
    ├── vergi-mufettisi/             # Vergi incelemesi hazırlığı
    └── yeminli-mali-musavir/        # YMM tasdik dosyası desteği
```

## Sınır

Bu yazılım ruhsatlı SMMM/YMM'nin imza, tasdik, beyan veya mesleki sorumluluğunun yerine geçmez. “Mükellef lehine” politika hukuka aykırı işlem, eksik/yanıltıcı kayıt, kanıt gizleme veya resmî/YMM tarafsızlığını bozma yetkisi vermez. Çıktılar dış gönderimden önce yetkili meslek mensubu tarafından incelenmelidir. Mevzuat değişkendir; her vaka tarihinde resmî kaynaklar yeniden ingest edilip yürürlük doğrulanmalıdır.

MIT — Copyright (c) 2026 Bayram Can Çapar.
