# Mali Müşavirim (`muhasebecim`)

Türk muhasebesi ve mali müşavirlik işleri için yerel veri işleyen, resmî kaynak sürümleyen ve bütün sayısal işlemleri denetlenebilir Python koduyla yapan Codex yeteneği.

## Teslim edilen sistem

- SMMM çalışma modeli: iş kabulü ve sözleşmeden belge akışı, kayıt, aylık kapanış, beyan, dönem sonu, raporlama ve devre kadar kontrol kapıları.
- TMS/TFRS, BOBİ FRS, KÜMİ FRS, VUK ve Tekdüzen/MSUGT için konu yönlendiricileri ve yürürlük politikası.
- Açık resmî kaynakları yerel korpusa alan, SHA-256 ile sürümleyen, metin çıkaran ve arayan ingest sistemi.
- Müşteri verisini cihaz dışına çıkarmayan yerel-only analiz politikası.
- `Decimal` tabanlı 14 işlemli hesap motoru: yevmiye denkliği, amortisman, bugünkü değer, etkin faiz, stok, kur, endeksleme, değer düşüklüğü, ertelenmiş vergi, ticari-mali kâr, KDV ve gün hesabı.
- Vaka klasörü açan ve işi “meslek mensubu incelemesine hazır” olana kadar deterministik çıkış kapılarıyla kontrol eden çalışma döngüsü.
- Otomatik testler ve 2 Ağustos 2026 tarihinde yeniden doğrulanmış, sürüm izli resmî kaynak korpusu.
- CSV/TSV/JSON/TXT, metin katmanlı PDF ve XLSX/XLSM müşteri kayıtlarını tamamen yerelde alan vaka ingest'i; elektronik tablo formülleri ve makroları çalıştırılmaz.

## Yerel veri garantisi

Kodlama dili Python 3.11+'dır. Müşteri belgesi, mizan, bordro, banka hareketi ve diğer vaka verileri uzak OCR, embedding, LLM veya analiz hizmetine gönderilmez. Ağ yalnızca manifestteki açık resmî kaynakları indirmek için kullanılır; çıkarım, indeksleme, arama ve hesaplama yerelde yapılır.

`cases/`, `corpus/` ve yaygın muhasebe veri dosyaları `.gitignore` ile GitHub dışında tutulur. Gerçek müşteri kayıtlarını hiçbir zaman kaynak kod deposuna eklemeyin.

## Hızlı kullanım

Testleri çalıştır:

```powershell
python .\skills\muhasebecim\scripts\test_muhasebecim.py
```

Resmî korpusu yenile ve denetle:

```powershell
python .\skills\muhasebecim\scripts\ingest_sources.py ingest `
  --manifest .\manifests\official-sources.json `
  --corpus .\corpus\official

python .\skills\muhasebecim\scripts\ingest_sources.py audit `
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

## Yapı

```text
muhasebecim/
├── corpus/official/                 # Yerel, hash denetimli başlangıç korpusu
├── manifests/official-sources.json  # Resmî kaynak manifesti
└── skills/muhasebecim/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/                  # Meslek, standart, VUK ve kontrol bilgisi
    └── scripts/                     # Python motorları ve testler
```

## Sınır

Bu yazılım ruhsatlı SMMM/YMM'nin imza, tasdik, beyan veya mesleki sorumluluğunun yerine geçmez. Çıktılar dış gönderimden önce yetkili meslek mensubu tarafından incelenmelidir. Mevzuat değişkendir; her vaka tarihinde resmî kaynaklar yeniden ingest edilip yürürlük doğrulanmalıdır.

MIT — Copyright (c) 2026 Bayram Can Çapar.
