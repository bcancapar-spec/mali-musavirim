# Deterministik Tekdüzen Hesap Planı ve VUK kayıt kontrolü

## Uygulama sınırı

Önce işletmenin genel MSUGT Tekdüzen Hesap Planına mı, yoksa banka, sigorta, katılım finans, finansal kiralama, faktoring, sermaye piyasası veya başka bir düzenleyicinin özel planına mı tabi olduğunu belirle. Genel plan dışındaki bir işletmeye bu katalogla otomatik uygunluk verme. `THP-SCOPE-001` bu durumda sonucu kapatır.

Motor kod ve kayıt biçimi uygunluğunu denetler; işlemin ekonomik özüne göre doğru hesabın seçildiğini, belgenin gerçekliğini veya vergi matrahının maddi doğruluğunu tek başına kanıtlamaz. Bunlar kanıt incelemesi ve mesleki muhakeme gerektirir.

## Sürümlü katalog

`scripts/data/thp_accounts.v1.json` genel plan için makinece okunabilir katalogdur. Katalog:

- 1-9 hesap sınıflarını ve tanımlı hesap gruplarını,
- üç haneli hesap köklerini, adlarını ve normal bakiye yönlerini,
- 11 Sıra No.lu MSUGT ile gelen finansal kiralama hesaplarını,
- 12 Sıra No.lu MSUGT ile gelen enflasyon düzeltmesi hesaplarını,
- 170-177 ve 350-357 proje hesabı aralıklarını,
- kaynak, yürürlük, kapsam ve ikincil meslek kuruluşu çapraz kontrolünü

sürüm ve SHA-256 özetiyle taşır. `524` hesabı yalnızca ikincil meslek kuruluşu çapraz kontrolüyle etiketlenmiştir; birincil düzenleme zinciri ayrıca meslek mensubu tarafından doğrulanmalıdır.

Katalog denetimini çalıştır:

```powershell
python scripts/thp_rule_engine.py catalog-audit
```

Katalogda olmayan 1-7 sınıfı kodlar fail-closed olarak `BLOCK` olur. Planın boş bıraktığı kodu “standart hesap” gibi sunma. 8 ve 9 sınıfları işletmeye özgü olduğundan `allow_custom_8_9` politikası ve boş olmayan hesap adı gerekir.

## İşlemler

Motor üç veri kontrolü sağlar:

```powershell
python scripts/thp_rule_engine.py account-validate --input accounts.json --output result.json
python scripts/thp_rule_engine.py journal-validate --input journal.json --output result.json
python scripts/thp_rule_engine.py trial-balance-validate --input trial-balance.json --output result.json
```

Örnek girdi üretmek için ilgili komuta `--example` ver. Komut çıktı kodları sabittir:

| Kod | Anlam |
|---:|---|
| 0 | `PASS` veya `PASS_WITH_WARNINGS` |
| 1 | Girdi geçerli fakat en az bir iş kuralı `BLOCK` |
| 2 | Kapalı şema, katalog veya sistem hatası |

Her sonuç; motor ve katalog sürümü, katalog ve girdi SHA-256 özeti, karar, sıralanmış bulgular, değerlendirilen kural kimlikleri ve çıktı üzerinde hesaplanan `receipt_sha256` içerir. Çalışma anı damgası kullanılmaz; aynı katalog ve aynı girdi aynı kanonik sonucu üretir.

## THP kural kapıları

| Kural ailesi | Denetim |
|---|---|
| `THP-SCOPE` | Genel planın sektörel özel plana yanlış uygulanmasını engeller. |
| `THP-CODE` | Hesap kökünü sürümlü katalog veya izin verilen 8/9 politikasına bağlar. |
| `THP-NAME` | Hesap adını Türkçe normalleştirme ve sınırlı açık alias listesiyle doğrular. |
| `THP-EFFECTIVE` | Hesabın analiz tarihinde yürürlükte olup olmadığını denetler. |
| `THP-COST` | 70-78 gruplarını 7/A, 79 grubunu 7/B seçeneğine bağlar. |
| `THP-JOURNAL` | Satır borç/alacak ayrıklığı ve yevmiye denkliğini denetler. |
| `THP-TRIAL` | Açılış-hareket-kapanış devrini ve mizan çapraz toplamlarını doğrular. |
| `THP-NORMAL-BALANCE` | Ters bakiye anomalilerini uyarı veya sıkı politikada blok olarak üretir. |

Parasal girdiler JSON sayı değil, ondalık dizge olmalıdır. Motor `Decimal` kullanır; `float`, negatif tutar, boş dizi, bilinmeyen alan ve tanımsız enum değeri şema hatasıdır.

## VUK kayıt kural kapıları

Motor, 213 sayılı Kanunun konsolide metnindeki açık ve mekanik olarak sınanabilir alt kümeyi uygular:

| Dayanak | Kural |
|---|---|
| VUK 215 | Türkçe kayıt; TRY dışı defter için açık izin kanıtı; yabancı para belgede TRY karşılığı/foreign-customer istisnası. |
| VUK 217 | Hatalı kaydın muhasebe usulüyle düzeltimi; silme ve okunamaz hâle getirme yasağı. |
| VUK 218 | Sağlanan yevmiye ve satır numaralarında tekrar ve boşluk kontrolü. |
| VUK 219 | Doğrudan kayıtta 10 gün; yetkili muhasebe fişinde 10 günlük fiş ve 45 günlük ana deftere aktarım; günlük kayıt zorunluluğu. |
| VUK 227 | Üçüncü kişilerle ilişkili kayıtlar için belge türü ve numarasıyla tevsik kapısı. |

VUK 215 kapsamındaki yabancı para defter izninin değişebilen eşik ve şartları kod içine alınmaz. `foreign_currency_permission=true` tek başına yetmez; `permission_source` ile olaya özgü resmî izin/dayanak verilmelidir.

## Vaka akışına bağlama

Genel plan kapsamındaki gerçek mizan veya yevmiye analizinde `case.json` içinde:

```json
{
  "requires_thp_validation": true
}
```

işaretini kullan ve motor çıktısını `outputs/thp-validation-result.json` yoluna yaz. `case_workflow.py`, kararın geçmesini ve `receipt_sha256` bütünlüğünü doğrulamadan vakayı meslek mensubu incelemesine hazır saymaz.

## Kaynak hiyerarşisi

1. Birincil: Resmî Gazete’de yayımlanan MSUGT metni ve Mevzuat Bilgi Sistemi’ndeki konsolide VUK.
2. Resmî indeks/kapsam: GİB’in MSUGT mevzuat kaydı.
3. Çapraz kontrol: İSMMMO Tekdüzen Hesap Planı dokümanı; birincil kaynak yerine geçmez.

Başlangıç bağlantıları:

- [GİB — 1 Sıra No.lu MSUGT](https://gib.gov.tr/mevzuat/kanun/434/teblig/7864)
- [Mevzuat Bilgi Sistemi — 213 sayılı VUK](https://www.mevzuat.gov.tr/mevzuatmetin/1.4.213.pdf)
- [İSMMMO — Tekdüzen Hesap Planı çapraz kontrolü](https://www.ismmmo.org.tr/dosya/415/Mevzuat-Dosya/tekduzhesapplani.pdf)

Son katalog doğrulama tarihi: 2 Ağustos 2026. Yeni vakada işlem tarihi ve sonraki değişiklikler yeniden doğrulanmalıdır.
