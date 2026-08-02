# Mali Müşavirim (`muhasebecim`)

Türk muhasebesi ve mali müşavirlik işleri için yerel veri işleyen, resmî kaynak sürümleyen ve bütün sayısal işlemleri denetlenebilir Python koduyla yapan Codex yeteneği.

**İlk public pilot sürüm:** `v0.0.1`

Mali müşavir açısından sistemin ne yaptığını, hangi verinin nasıl hazırlanacağını, THP/VUK bulgularının nasıl okunacağını ve gerçek veri testinin nasıl yürütüleceğini öğrenmek için [Mali Müşavir Kullanım Rehberi](docs/MALI-MUSAVIR-KULLANIM-REHBERI.md) ile başlayın.

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

## Yapı

```text
muhasebecim/
├── docs/                            # Mali müşavir kullanım rehberi
├── corpus/official/                 # Yerel, hash denetimli başlangıç korpusu
├── manifests/official-sources.json  # Resmî kaynak manifesti
└── skills/muhasebecim/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/                  # Meslek, standart, VUK ve kontrol bilgisi
    └── scripts/                     # Python motorları, THP kataloğu ve testler
```

## Sınır

Bu yazılım ruhsatlı SMMM/YMM'nin imza, tasdik, beyan veya mesleki sorumluluğunun yerine geçmez. Çıktılar dış gönderimden önce yetkili meslek mensubu tarafından incelenmelidir. Mevzuat değişkendir; her vaka tarihinde resmî kaynaklar yeniden ingest edilip yürürlük doğrulanmalıdır.

MIT — Copyright (c) 2026 Bayram Can Çapar.
