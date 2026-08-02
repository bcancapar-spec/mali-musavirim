# Mali Müşavirim v0.0.3 — Mali Müşavir Kullanım Rehberi

Bu rehber, sistemi yazılımcı gözüyle değil; defter, yevmiye, mizan, belge ve dönem sonu kontrolü yapan mali müşavirin iş akışıyla açıklar.

## İçindekiler

1. [Sistem ne işe yarar?](#1-sistem-ne-işe-yarar)
2. [Sistem neyin yerine geçmez?](#2-sistem-neyin-yerine-geçmez)
3. [v0.0.3 sürümünde bulunan bileşenler](#3-v003-sürümünde-bulunan-bileşenler)
4. [Dayanaklar ve kapsam](#4-dayanaklar-ve-kapsam)
5. [Kurulum ve ilk kontrol](#5-kurulum-ve-ilk-kontrol)
6. [Bir muhasebe işi nasıl yürütülür?](#6-bir-muhasebe-işi-nasıl-yürütülür)
7. [Hesap planı kontrolü](#7-hesap-planı-kontrolü)
8. [Yevmiye ve VUK kayıt kontrolü](#8-yevmiye-ve-vuk-kayıt-kontrolü)
9. [Mizan kontrolü](#9-mizan-kontrolü)
10. [Sonuçların okunması](#10-sonuçların-okunması)
11. [Kural kimliklerinin anlamı](#11-kural-kimliklerinin-anlamı)
12. [Vaka tamamlama kapısı](#12-vaka-tamamlama-kapısı)
13. [Müşteri verisi ve yerel çalışma](#13-müşteri-verisi-ve-yerel-çalışma)
14. [Hesaplama motoru](#14-hesaplama-motoru)
15. [Denetim izi ve hash değerleri](#15-denetim-izi-ve-hash-değerleri)
16. [Örnek çalışma senaryoları](#16-örnek-çalışma-senaryoları)
17. [Sınırlar ve mesleki inceleme](#17-sınırlar-ve-mesleki-inceleme)
18. [Gerçek veri testi öncesi kontrol listesi](#18-gerçek-veri-testi-öncesi-kontrol-listesi)
19. [Sürümleme yöntemi](#19-sürümleme-yöntemi)

## 1. Sistem ne işe yarar?

Mali Müşavirim; muhasebe verisini yerelde inceleyen, hesapları Python ile yapan ve her kontrolün sonucunu tekrar üretilebilir bir JSON dosyasında saklayan yardımcı sistemdir.

Temel amacı şunlardır:

- Genel Tekdüzen Hesap Planındaki hesap kodlarını ve hesap adlarını kontrol etmek.
- İşletmenin genel plana mı, sektörel özel plana mı tabi olduğunu ayırmak.
- 7/A ve 7/B maliyet hesaplarının birbiriyle karıştırılmasını önlemek.
- Yevmiye kayıtlarında borç/alacak denkliğini sınamak.
- VUK'un kayıt dili, para birimi, düzeltme, sıra, kayıt zamanı ve tevsik hükümlerinin makinece kontrol edilebilen kısmını sınamak.
- Mizanın açılış, dönem hareketi ve kapanış bakiyelerini mutabıklaştırmak.
- Amortisman, stok, KDV, kur, bugünkü değer, etkin faiz ve ticari-mali kâr gibi sayısal işlemleri Python ile yapmak.
- Kullanılan girdi, hesaplama, kaynak ve sonucu denetim iziyle korumak.
- Her vakada hukuka uygun mükellef lehine adım hazırlamak; aleyhe hususu kullanıcı/SMMM/YMM'ye yerel iç kayıtla bildirmek.
- Eksik veya hatalı bir kontrol varken işi sessizce “uygun” saymamak.

Sistemin temel yaklaşımı şudur:

> Olgu → uygulanacak hüküm → Python kontrolü/hesabı → bulgu → meslek mensubu değerlendirmesi.

## 2. Sistem neyin yerine geçmez?

Sistem aşağıdaki mesleki sorumlulukların yerine geçmez:

- SMMM veya YMM imzası,
- beyanname gönderme yetkisi,
- tasdik,
- belgenin gerçekliğinin tespiti,
- muvazaa veya sahte belge incelemesi,
- işlemin ekonomik özüne göre nihai hesap seçimi,
- vergi incelemesi sonucu veya ceza doğmayacağı yönünde güvence,
- işletmeye özgü sözleşme, özelge ve yargı kararı değerlendirmesi.

`PASS` kararı, “beyanname doğrudur” anlamına gelmez. Yalnızca gönderilen verinin tanımlı mekanik kontrolleri geçtiğini gösterir.

## 3. v0.0.3 sürümünde bulunan bileşenler

| Bileşen | Mali müşavir açısından görevi |
|---|---|
| `thp_rule_engine.py` | Hesap, yevmiye, VUK kayıt düzeni ve mizan kontrolü |
| `thp_accounts.v1.json` | Sürümlü genel THP hesap kataloğu |
| `muhasebecim_engine.py` | Sayısal muhasebe ve vergi hesaplamaları |
| `case_workflow.py` | Bir işin tamamlanma kapılarını takip eden vaka dosyası |
| `ingest_sources.py` | Belge ve resmî kaynakları yerel korpusa alma |
| `query_corpus.py` | Yerel korpusta metin arama |
| `prepare_2026_tfrs_manifest.py` | İlgili 2026 TMS/TFRS tam metinlerini seçme |
| `professional_role_engine.py` | Vergi incelemesi ve YMM tasdik yetki/kalite kapıları |
| `professional_roles.v1.json` | 17 kaynağa bağlı 48 sürümlü rol kuralı |
| `taxpayer_interest_engine.py` | Lehe adım ve aleyhe iç bildirim için kapatılamayan vaka kapısı |
| `taxpayer_interest_rules.v1.json` | 5 kaynak kaydına bağlı 16 sürümlü mükellef menfaati kuralı |
| `test_*.py` | 72 pozitif, negatif, kurcalama ve entegrasyon testi |
| `test_suite_report.py` | Test sayısı ve geçiş sonucunu yeniden üreten JSON rapor aracı |

Testlerin dosya bazlı sayısı, yöntemi ve güvence sınırları [Test Yöntemi ve Doğrulama Sonuçları](TEST-YONTEMI-VE-SONUCLARI.md) belgesinde açıklanır.

THP kataloğunda 271 tanımlı hesap kökü, 170-177 ve 350-357 proje hesabı aralıkları, hesap adları, normal bakiye yönleri ve kaynak bağları bulunur.

## 4. Dayanaklar ve kapsam

### Genel Tekdüzen Hesap Planı

Katalog genel MSUGT Tekdüzen Hesap Planı içindir. Banka, sigorta, katılım finans, finansal kiralama, faktoring, sermaye piyasası işletmeleri ve özel düzenleyici hesap planına tabi diğer işletmeler için otomatik olarak uygulanmaz.

Sektör `general` dışında seçildiğinde motor `THP-SCOPE-001` bulgusu üretir ve genel plan sonucunu `BLOCK` eder.

### VUK kayıt düzeni

v0.0.3 sürümü aşağıdaki maddelerin açık ve mekanik olarak kontrol edilebilen kısmını kapsar:

| VUK maddesi | Motorun kontrol ettiği konu |
|---:|---|
| 215 | Türkçe kayıt, defter para birimi, yabancı para belgede TRY karşılığı |
| 217 | Yanlış kayıtların muhasebe usulüyle düzeltilmesi; silme/üzerine yazma yasağı |
| 218 | Sağlanan yevmiye-satır numaralarında tekrar ve boşluk kontrolü |
| 219 | Doğrudan kayıtta 10 gün, yetkili fişte 10/45 gün, günlük kayıt zorunluluğu |
| 227 | Üçüncü kişilerle ilgili kayıtların belge türü ve belge numarasıyla tevsiki |

Değişken parasal had, oran, kur ve izin şartları kod içine sabit yazılmaz. İşlem tarihi için doğrulanan değer ve resmî kaynak ayrıca girdi olarak tutulur.

### Finansal raporlama ile vergi katmanı

TMS/TFRS, BOBİ FRS veya KÜMİ FRS sonucu ile VUK/MSUGT sonucu aynı şey değildir. Sistem bu iki katmanı ayrı ele alır:

- Finansal raporlama katmanı: finansal tablonun ilgili standarda göre ölçüm ve sunumu.
- Vergi katmanı: VUK değerleme ve vergi matrahı etkisi.
- Mutabakat: geçici fark, sürekli fark, ilave ve indirimlerin açıklanması.

## 5. Kurulum ve ilk kontrol

Gereken ortam:

- Python 3.11 veya üzeri,
- Windows PowerShell veya eşdeğer terminal,
- bu GitHub reposunun yerel kopyası.

Repo ana dizininde önce sürümü kontrol et:

```powershell
python -c "import tomllib, pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
```

Beklenen sonuç:

```text
0.0.3
```

Katalog bütünlüğünü kontrol et:

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py catalog-audit
```

`decision` alanının `PASS` olması gerekir.

Tüm otomatik testleri çalıştır:

```powershell
python -m unittest discover -s .\skills\muhasebecim\scripts -p "test_*.py" -v
```

## 6. Bir muhasebe işi nasıl yürütülür?

### A. Kapsamı belirle

İşe başlamadan önce aşağıdaki sorular cevaplanır:

1. İncelenen işletme kimdir?
2. İşlem tarihi ve hesap dönemi nedir?
3. İşletme genel THP'ye mi, özel hesap planına mı tabidir?
4. Amaç yasal defter, vergi hesabı, finansal raporlama veya yönetim raporu mudur?
5. TMS/TFRS, BOBİ FRS veya KÜMİ FRS uygulanıyor mu?
6. Önemlilik seviyesi nedir?
7. Eksik belge veya sonucu etkileyen açık husus var mıdır?

### B. Vaka klasörünü aç

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py init `
  --case .\cases\ornek-ltd-2026 `
  --case-id ornek-ltd-2026 `
  --as-of 2026-08-02
```

Bu işlem aşağıdaki çalışma alanlarını oluşturur:

- `documents/`: müşteri belgeleri,
- `calculations/`: Python girdi ve sonuçları,
- `workpapers/`: muhakeme ve çalışma kâğıtları,
- `outputs/`: sonuç ve kontrol dosyaları,
- `corpus/`: yalnız o vakaya ait yerel belge korpusu.

### C. Olguları ve kaynakları kaydet

`facts.json` içinde dönem, işletme tipi, amaç, çerçeve, para birimi, varsayımlar ve açık hususlar tamamlanır. `sources.json` içinde kullanılan mevzuatın kurumu, başlığı, URL'si, durumu, erişim tarihi ve nokta atfı saklanır.

### D. Hesapları Python ile yap

Elle bulunan bir toplam nihai doğruluk kaynağı sayılmaz. Tutarlar JSON dizgesi olarak Python'a verilir:

```json
{
  "amount": "120000.00",
  "rate": "0.20"
}
```

`120000.00` gibi değerlerin tırnak içinde olmasının nedeni ikili `float` yuvarlama hatasını önlemektir.

### E. THP/VUK kontrolünü çalıştır

Yevmiye veya mizan verisi için aşağıdaki bölümlerdeki uygun işlem seçilir.

### F. Ticari-mali mutabakatı hazırla

Finansal raporlama sonucu ile vergi sonucu farklıysa farklar satır bazında açıklanır. Kanunen kabul edilmeyen giderler, istisna/indirimler, geçici ve sürekli farklar birbirinden ayrılır.

### G. Tamamlama kapısını çalıştır

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py check --case .\cases\ornek-ltd-2026
python .\skills\muhasebecim\scripts\case_workflow.py finalize --case .\cases\ornek-ltd-2026
```

`finalize`, yalnızca tanımlı kontroller geçtiğinde vakayı `ready_for_professional_review` yapar. Bu durum “gönderildi” veya “mesleki olarak onaylandı” anlamına gelmez.

## 7. Hesap planı kontrolü

Bu işlem yalnız hesap kodu/adı listesini denetlemek için kullanılır.

### Örnek girdi

```json
{
  "schema_version": 1,
  "as_of_date": "2026-08-02",
  "entity": {
    "sector": "general",
    "chart": "MSUGT_THP_GENERAL",
    "cost_method": "7A"
  },
  "accounts": [
    {"account_code": "100.01", "account_name": "Kasa"},
    {"account_code": "120", "account_name": "Alıcılar"},
    {"account_code": "391", "account_name": "Hesaplanan KDV"}
  ]
}
```

### Alanların anlamı

| Alan | Açıklama |
|---|---|
| `as_of_date` | Hesabın bu tarih itibarıyla yürürlük kontrolünde kullanılacak tarih |
| `sector` | `general` veya tanımlı özel sektörlerden biri |
| `chart` | Genel plan için `MSUGT_THP_GENERAL` |
| `cost_method` | `7A`, `7B` veya maliyet hesabı yoksa `none` |
| `account_code` | Üç haneli kök veya `100.01` gibi alt hesap; mutlaka metin |
| `account_name` | Defter/mizanda görülen hesap adı |

### Çalıştırma

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py account-validate `
  --input .\accounts.json `
  --output .\accounts-result.json
```

Motor şunları kontrol eder:

- hesap kökü katalogda var mı,
- hesap adı katalogla uyumlu mu,
- hesap analiz tarihinde yürürlükte mi,
- 7/A ve 7/B tercihiyle uyumlu mu,
- işletme genel plan kapsamında mı,
- 8/9 sınıfındaki işletmeye özgü hesap politikası izin veriyor mu,
- aynı hesap kodu iki kez gönderilmiş mi.

## 8. Yevmiye ve VUK kayıt kontrolü

Bu işlem, hesap planı denetimine kayıt düzeni ve VUK kontrollerini ekler.

### Örnek girdi

```json
{
  "schema_version": 1,
  "as_of_date": "2026-08-02",
  "entity": {
    "sector": "general",
    "chart": "MSUGT_THP_GENERAL",
    "cost_method": "7A",
    "ledger_currency": "TRY",
    "language": "tr"
  },
  "entries": [
    {
      "journal_no": "YEV-2026-0001",
      "line_no": 1,
      "transaction_date": "2026-08-01",
      "ledger_date": "2026-08-02",
      "recording_basis": "direct_ledger",
      "account_code": "102.01",
      "account_name": "Bankalar",
      "description": "Müşteri tahsilatı",
      "debit": "10000.00",
      "credit": "0",
      "counterparty_relation": "third_party",
      "document_type": "banka dekontu",
      "document_no": "MASKELI-0001"
    },
    {
      "journal_no": "YEV-2026-0001",
      "line_no": 2,
      "transaction_date": "2026-08-01",
      "ledger_date": "2026-08-02",
      "recording_basis": "direct_ledger",
      "account_code": "120.01",
      "account_name": "Alıcılar",
      "description": "Müşteri tahsilatı",
      "debit": "0",
      "credit": "10000.00",
      "counterparty_relation": "third_party",
      "document_type": "banka dekontu",
      "document_no": "MASKELI-0001"
    }
  ]
}
```

### Kayıt alanlarının anlamı

| Alan | Açıklama |
|---|---|
| `journal_no` | Aynı fişe ait satırları bir araya getiren yevmiye/fiş numarası |
| `line_no` | Fiş içindeki sıra numarası; 1'den başlamalı ve boşluk bırakmamalı |
| `transaction_date` | İşlemin ekonomik/belgesel tarihi |
| `ledger_date` | Deftere kayıt tarihi |
| `voucher_date` | Yetkili muhasebe fişi kullanılıyorsa fiş tarihi |
| `recording_basis` | `direct_ledger`, `authorized_voucher` veya `daily_required` |
| `debit`, `credit` | Negatif olmayan ondalık metin; aynı satırda yalnız biri sıfırdan büyük olabilir |
| `counterparty_relation` | `third_party`, `internal` veya `unknown` |
| `document_type` | Fatura, dekont, makbuz vb. belge türü |
| `document_no` | Belge numarası; örnek ve loglarda maskeleme önerilir |
| `document_currency` | Belgenin ISO para kodu; varsayılan `TRY` |
| `try_equivalent_present` | Yabancı para belgede TRY karşılığı bulunup bulunmadığı |
| `foreign_customer` | Yabancı müşteriye düzenlenen belge istisnasının olgu alanı |
| `turkish_record_present` | Ana dil `other` ise Türkçe kayıt karşılığının bulunup bulunmadığı |
| `correction_of` | Düzeltilen eski kayıt/fiş referansı |
| `correction_method` | `reversal_entry` veya `accounting_correction`; `erase` ve `overwrite` bloklanır |

### Çalıştırma

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py journal-validate `
  --input .\journal.json `
  --output .\journal-result.json
```

### Süre kontrolünün yorumu

- `direct_ledger`: işlem ile deftere kayıt arasında 10 günden fazla süre varsa blok.
- `authorized_voucher`: yetkili fişin 10 gün içinde hazırlanması ve ana deftere aktarımın 45 günü geçmemesi gerekir.
- `daily_required`: işlem ve kayıt tarihi aynı gün olmalıdır.

Süreler Python `date` hesabıyla bulunur; elle gün sayımı yapılmaz.

## 9. Mizan kontrolü

Mizan kontrolü her hesabın hareket denklemini ve genel toplamları birlikte sınar.

Her hesap için uygulanan denklem:

```text
Açılış neti + dönem borç hareketi - dönem alacak hareketi = kapanış neti
```

### Örnek girdi

```json
{
  "schema_version": 1,
  "as_of_date": "2026-08-02",
  "entity": {
    "sector": "general",
    "chart": "MSUGT_THP_GENERAL",
    "cost_method": "7A"
  },
  "accounts": [
    {
      "account_code": "100",
      "account_name": "Kasa",
      "opening_debit": "0",
      "opening_credit": "0",
      "period_debit": "10000.00",
      "period_credit": "0",
      "closing_debit": "10000.00",
      "closing_credit": "0"
    },
    {
      "account_code": "500",
      "account_name": "Sermaye",
      "opening_debit": "0",
      "opening_credit": "0",
      "period_debit": "0",
      "period_credit": "10000.00",
      "closing_debit": "0",
      "closing_credit": "10000.00"
    }
  ]
}
```

### Çalıştırma

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py trial-balance-validate `
  --input .\trial-balance.json `
  --output .\trial-balance-result.json
```

Kontroller:

- açılış borç ve alacak toplamı,
- dönem borç ve alacak hareket toplamı,
- kapanış borç ve alacak toplamı,
- hesap bazında açılış-hareket-kapanış devri,
- aynı hesapta hem borç hem alacak bakiyesi gösterilmesi,
- normal bakiye yönünün tersine dönen hesaplar,
- hesap kodu, adı, sektör ve 7/A-7/B uygunluğu.

Ters normal bakiye varsayılan olarak `WARN` üretir. `strict_normal_balance=true` seçeneğiyle `BLOCK` yapılabilir. Çünkü ters bakiye her zaman hata değildir; avans, mahsup, virman veya dönemsel durumdan kaynaklanabilir ve mesleki inceleme ister.

## 10. Sonuçların okunması

Her sonuç dosyasının ana alanları:

| Alan | Anlamı |
|---|---|
| `engine.version` | Çalışan yazılım sürümü; v0.0.3 için `0.0.3` |
| `catalog.version` | Kullanılan mevzuat/hesap kataloğunun ayrı sürümü |
| `catalog.sha256` | Katalog dosyasının parmak izi |
| `input_sha256` | Girdinin kanonik parmak izi |
| `decision` | `PASS`, `PASS_WITH_WARNINGS`, `BLOCK` veya `ERROR` |
| `findings` | Kural kimliği, önem seviyesi, konum, açıklama ve kaynaklar |
| `evaluated_rule_ids` | Kontrol setinde değerlendirilen kurallar |
| `result` | Normalize edilmiş kayıtlar, toplamlar ve denklik sonuçları |
| `receipt_sha256` | Sonuç dosyasının kurcalanıp kurcalanmadığını sınayan makbuz özeti |

### Kararların anlamı

- `PASS`: Tanımlı kurallar içinde blok veya uyarı yok.
- `PASS_WITH_WARNINGS`: Mekanik kontroller geçti; meslek mensubunun incelemesi gereken anomali veya ikincil kaynak uyarısı var.
- `BLOCK`: En az bir iş kuralı ihlali var. Hata düzeltilmeden uygunluk sonucu kullanılmamalı.
- `ERROR`: Girdi şeması, veri tipi, katalog veya sistem hatası var; muhasebe sonucu üretilmiş sayılmaz.

### Komut çıkış kodları

| Çıkış kodu | Anlamı |
|---:|---|
| 0 | `PASS` veya `PASS_WITH_WARNINGS` |
| 1 | `BLOCK` |
| 2 | `ERROR` |

## 11. Kural kimliklerinin anlamı

### THP kuralları

| Kural | Açıklama |
|---|---|
| `THP-SCOPE-001` | İşletme genel plan kapsamında değil |
| `THP-CODE-001` | Hesap kökü sürümlü katalogda yok |
| `THP-NAME-001` | Hesap adı katalogla uyuşmuyor |
| `THP-EFFECTIVE-001` | Hesap analiz tarihinde yürürlükte değil |
| `THP-COST-001` | 7/A hesabı yanlış maliyet seçeneğiyle kullanılmış |
| `THP-COST-002` | 7/B hesabı yanlış maliyet seçeneğiyle kullanılmış |
| `THP-SOURCE-001` | Hesap yalnız ikincil profesyonel çapraz kaynağa dayanıyor |
| `THP-LINE-001` | Satırda hem borç/alacak var veya ikisi de sıfır |
| `THP-JOURNAL-BALANCE-001` | Fiş borç ve alacak toplamı eşit değil |
| `THP-TRIAL-ROLLFORWARD-001` | Hesap kapanış bakiyesi hareketlerden türemiyor |
| `THP-TRIAL-TOTAL-001` | Mizan borç/alacak toplamı eşit değil |
| `THP-NORMAL-BALANCE-001` | Hesap katalogdaki normal bakiye yönünün tersinde |

### VUK kuralları

| Kural | Açıklama |
|---|---|
| `VUK-215-LANGUAGE-001` | Türkçe kayıt koşulu sağlanmamış |
| `VUK-215-CURRENCY-001` | TRY dışı defter için açık izin ve kaynak yok |
| `VUK-215-DOCUMENT-001` | Yabancı para belgede TRY karşılığı/istisna bilgisi yok |
| `VUK-217-CORRECTION-*` | Düzeltme yöntemi veya eski kayıt referansı uygun değil |
| `VUK-218-SEQUENCE-*` | Satır tekrarı veya sıra boşluğu var |
| `VUK-219-DIRECT-001` | Doğrudan kayıt 10 günü aşmış |
| `VUK-219-VOUCHER-*` | Yetkili fişin 10/45 günlük koşulu sağlanmamış |
| `VUK-219-DAILY-001` | Günlük tutulması gereken kayıt aynı gün yapılmamış |
| `VUK-227-TEVSIK-001` | Üçüncü kişi işleminin belge türü/numarası yok |
| `VUK-227-TEVSIK-002` | Karşı taraf ilişkisi bilinmediğinden inceleme gerekiyor |

## 12. Vaka tamamlama kapısı

Genel THP/VUK kontrolü zorunlu bir vakada `case.json` içinde şu alan açılır:

```json
{
  "requires_thp_validation": true
}
```

Motor sonucu şu yola yazılır:

```text
outputs/thp-validation-result.json
```

Vaka kapısı aşağıdakileri kontrol eder:

- doğru motor tarafından üretilmiş olması,
- işlemin hesap, yevmiye veya mizan kontrolü olması,
- kararın `PASS` veya `PASS_WITH_WARNINGS` olması,
- `receipt_sha256` değerinin sonuç içeriğiyle eşleşmesi.

Sonuç dosyasında daha sonra bir tutar değiştirilirse makbuz geçersiz olur ve vaka kapısı kapanır.

## 13. Müşteri verisi ve yerel çalışma

Müşteri verileri için temel ilke:

> Mizan, yevmiye, banka hareketi, bordro ve belge içeriği analiz amacıyla internet hizmetine gönderilmez.

Yerel ingest sistemi şunları destekler:

- CSV,
- TSV,
- JSON,
- TXT,
- metin katmanlı PDF,
- XLSX ve XLSM.

Elektronik tablo formülleri ve makroları çalıştırılmaz. Formül metni korunabilir ancak muhasebe doğruluğu için sonuç yeniden Python ile hesaplanır.

`scope: case` olan müşteri manifestinde HTTP/HTTPS kaynağı kabul edilmez. Müşteri dosyası yerel yol olmalıdır. Açık resmî mevzuat kaynakları ise ayrı `scope: public` korpusunda tutulur.

`cases/` ve `corpus/` Git tarafından yok sayılır. Gerçek müşteri verisi GitHub'a eklenmemelidir.

Excel veya muhasebe programı çıktısı doğrudan motor şemasına uymuyorsa vakaya özel bir Python dönüştürücü yazılır. Dönüştürücü:

1. sütun eşlemesini açıkça gösterir,
2. tarih ve tutar dönüşümlerini kaydeder,
3. eksik alanları raporlar,
4. kaynak dosya SHA-256 özetini saklar,
5. motor için JSON üretir.

v0.0.3 her muhasebe programının özel Excel kolonlarını kendiliğinden tahmin etmez. İlk gerçek veri testinde kolon eşlemesi meslek mensubuyla doğrulanmalıdır.

## 14. Hesaplama motoru

Hazır hesapları listele:

```powershell
python .\skills\muhasebecim\scripts\muhasebecim_engine.py --list
```

v0.0.3 kapsamındaki hesaplamalar:

- yevmiye borç/alacak denkliği,
- normal amortisman,
- azalan bakiyeler amortismanı,
- bugünkü değer,
- etkin faiz,
- hareketli ağırlıklı ortalama stok,
- FIFO stok,
- kur değerlemesi,
- endeksleme,
- değer düşüklüğü,
- ertelenmiş vergi,
- ticari kârdan mali kâra geçiş,
- KDV ayrıştırması,
- gün hesabı.

Örnek girdi görmek için:

```powershell
python .\skills\muhasebecim\scripts\muhasebecim_engine.py vat --example
```

Hesaplamalarda `Decimal` ve açık yuvarlama yöntemi kullanılır. Kur, oran, endeks veya yıllık had gibi değişen veriler motor içine kalıcı yazılmaz; kaynak meta verisiyle girdiye eklenir.

## 15. Denetim izi ve hash değerleri

Hash, bir dosyanın içeriğine ait dijital parmak izidir. Aynı içerik aynı hash'i; değişen içerik farklı hash'i üretir.

Sistemde üç temel hash kullanılır:

1. `catalog.sha256`: hangi hesap planı dosyasının kullanıldığını gösterir.
2. `input_sha256`: hangi girdinin kontrol edildiğini gösterir.
3. `receipt_sha256`: sonuç dosyasının sonradan değiştirilip değiştirilmediğini gösterir.

Bu değerler elektronik imza değildir. Ancak çalışma kâğıdında “hangi dosya, hangi motor ve hangi katalogla işlendi?” sorusunu cevaplayan teknik denetim izidir.

## 16. Örnek çalışma senaryoları

### Senaryo 1 — Yanlış hesap kodu

Mizanda `339 Diğer Çeşitli Borçlar` gönderilirse katalogda standart hesap olmadığı için `THP-CODE-001` ve `BLOCK` oluşur. Genel plandaki ilgili standart kök `336` olarak ayrıca değerlendirilmelidir; motor ekonomik işlemi görmeden otomatik virman önermez.

### Senaryo 2 — 7/A işletmesinde 790 hesabı

İşletme `cost_method: 7A` iken `790` kullanılırsa `THP-COST-002` oluşur. Kayıt düzeltilmeden geçiş verilmez.

### Senaryo 3 — On bir gün sonra kayıt

`recording_basis: direct_ledger` olan işlemde kayıt tarihi işlem tarihinden 11 gün sonraysa `VUK-219-DIRECT-001` oluşur.

### Senaryo 4 — Belgesiz üçüncü kişi işlemi

`counterparty_relation: third_party` olduğu hâlde belge türü veya numarası boşsa `VUK-227-TEVSIK-001` oluşur.

### Senaryo 5 — Mizan ters bakiye

Normalde borç bakiyesi veren `100 Kasa` alacak bakiye verirse varsayılan sonuç `PASS_WITH_WARNINGS` olabilir. Bu durum kasanın fiilen eksi olamayacağı yönündeki mesleki incelemeyi tetikler; sıkı politikada bloklanabilir.

### Senaryo 6 — Sonuç dosyasının değiştirilmesi

Motor çıktısında bir toplam elle değiştirilirse `receipt_sha256` artık tutmaz. `case_workflow.py` THP/VUK kapısını geçirmez.

## 17. Sınırlar ve mesleki inceleme

v0.0.3 için açık sınırlar:

- Genel THP dışındaki sektörel planların hesap katalogları henüz motor içinde bulunmaz.
- Kod/ad uygunluğu işlemin ekonomik özüne göre doğru hesap seçildiğini kanıtlamaz.
- Belge türü ve numarası kontrol edilir; belgenin gerçekliği ve hukuki geçerliliği otomatik doğrulanmaz.
- VUK maddelerinin yalnız mekanik olarak sınanabilen alt kümesi uygulanır.
- Özelge, sözleşme, yargı kararı ve olaya özgü vergi yorumu mesleki muhakeme gerektirir.
- Değişken oran, had, kur ve endeks işlem tarihinde resmî kaynaktan yeniden doğrulanmalıdır.
- Hesap kataloğundaki `524 Maliyet Bedeli Artışları Fonu` için birincil değişiklik zinciri tamamlanıncaya kadar `THP-SOURCE-001` uyarısı üretilir.
- GİB'in MSUGT sayfası istemci taraflı çalıştığı için yerel metin çıkarımı `low_text` olabilir; bu durum korpus kalite uyarısında açıkça gösterilir.

## 18. Gerçek veri testi öncesi kontrol listesi

Mali müşavir aşağıdaki bilgileri hazırlar:

- [ ] İşletmenin unvanı yerine testte kullanılacak maskeli kimlik
- [ ] Vergi/hukuki işletme türü
- [ ] Genel THP veya özel hesap planı bilgisi
- [ ] Hesap dönemi başlangıç ve bitiş tarihi
- [ ] Mizan veya yevmiye dosyasının formatı
- [ ] Kolonların anlamı ve para birimi
- [ ] 7/A veya 7/B seçimi
- [ ] Açılış, dönem hareketi ve kapanış kolonları
- [ ] Yevmiye için işlem ve kayıt tarihi ayrımı
- [ ] Belge türü ve belge numarası kolonları
- [ ] Dövizli kayıt varsa belge/defter para birimi bilgisi
- [ ] Kişisel verilerin maskelenmesi
- [ ] Beklenen kontrol amacı ve önemlilik seviyesi

İlk test sırası:

1. Dosya yerel vaka klasörüne alınır.
2. Özgün dosyanın SHA-256 özeti çıkarılır.
3. Kolonlar mali müşavirle birlikte eşlenir.
4. Python dönüştürücü çalıştırılır.
5. Hesap kataloğu kontrolü yapılır.
6. Yevmiye veya mizan kontrolü çalıştırılır.
7. Bulgular `BLOCK`, `WARN` ve `INFO` olarak ayrılır.
8. Her bulgu için kaynak kayıt ve düzeltme kararı yazılır.
9. Düzeltilen veri yeniden çalıştırılır.
10. Sonuç ve makbuz vaka dosyasına alınır.

## 19. Sürümleme yöntemi

İki sürüm birlikte gösterilir:

- Yazılım sürümü: `0.0.3`
- THP katalog sürümü: `2026.08.02-1`

Bu ayrım bilinçlidir. Yazılımın kodu değişmeden mevzuat kataloğu güncellenebilir; veya mevzuat kataloğu aynı kalırken motor hatası düzeltilebilir. Her sonuç dosyası hem motor sürümünü hem katalog sürüm ve hash'ini taşır.

`v0.0.3`, `v0.0.2` vergi incelemesi/YMM kapılarına her vakada zorunlu mükellef lehine adım ve aleyhe hususta yerel iç bildirim katmanını ekler. Ayrıntılar için [Vergi Müfettişi ve YMM Uygulama Rehberi](VERGI-MUFETTISI-YMM-REHBERI.md) ile [Mükellef Menfaati ve İç Bildirim Rehberi](MUKELLEF-MENFAATI-VE-IC-BILDIRIM.md) dosyalarını okuyun. Dış gönderim ve mesleki onaydan önce bütün bulgular ruhsatlı veya yetkili meslek mensubu tarafından incelenmelidir.
