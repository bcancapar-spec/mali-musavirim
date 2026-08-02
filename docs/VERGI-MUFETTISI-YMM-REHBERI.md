# Vergi Müfettişi ve YMM Yetenekleri — v0.0.3 Uygulama Rehberi

Bu rehber, `muhasebecim` eklentisine eklenen vergi müfettişi bakışı ile Yeminli Mali Müşavir tasdik desteğinin ne yaptığını mali müşavir diliyle açıklar.

## 1. Kısa sonuç

v0.0.3 ile sistem üç ayrı uzmanlığı ve ortak mükellef menfaati/iç bildirim kapısını tek Codex eklentisi içinde toplar:

| Yetenek | Ne için kullanılır? | Yetki sonucu |
|---|---|---|
| `$muhasebecim` | Muhasebe, THP/VUK kayıt kontrolü, TMS/TFRS ve Python hesapları | Meslek mensubu incelemesine hazır taslak |
| `$vergi-mufettisi` | Vergi incelemesi hazırlığı, risk hipotezi, veri mutabakatı, kanıt ve bulgu dosyası | Kamu yetkisi kullanmayan inceleme/hazırlık taslağı |
| `$yeminli-mali-musavir` | YMM tasdik kabulü, bağımsızlık, sözleşme, denetim, karşıt inceleme ve rapor dosyası | İmza/mühür içermeyen YMM inceleme taslağı |

Bu ayrım bilerek yapılmıştır. Muhasebe hizmeti, kamu vergi inceleme yetkisi ve YMM tasdik sorumluluğu aynı iş değildir.

## 2. Mevzuattan çıkarılan vergi müfettişi yetenekleri

VUK 134'e göre vergi incelemesinin amacı, ödenmesi gereken vergilerin doğruluğunu araştırmak, tespit etmek ve sağlamaktır. Eklenti bu amacı şu analitik yeteneklere dönüştürür:

- Görev, konu, gerekçe, vergi türü, dönem ve inceleme türü kapsamı kurma.
- Riskleri kesin iddia yerine test edilebilir hipotezlere ayırma.
- Defter, yevmiye, kebir, mizan, mali tablo, beyanname, tahakkuk, ödeme, e-belge ve uygun üçüncü taraf verisini zincir halinde mutabıklaştırma.
- Yazılı bilgi-belge taleplerinin kapsamını ve teslim izini izleme.
- Kanıtın kaynağını, SHA-256 özetini, elde edilme tarihini ve bulguyla bağını koruma.
- Örneklem evreni, yöntemi, tohum/başlangıç ve seçim izini Python ile kaydetme.
- Lehe ve aleyhe kanıtı birlikte değerlendirme.
- Mükellef itiraz ve mülahazalarını yoruma karıştırmadan saklama.
- Bulguyu olgu, mevzuat, hesap, kanıt, açıklama ve sonuç zincirinde kurma.
- VUK 359 emaresini suçluluk sonucu değil, yetkili incelemeye eskalasyon bayrağı olarak işaretleme.
- Mükellef hakları, vergi mahremiyeti, süre ve rapor kalite kapılarını izleme.

VDK'nın resmî görev listesinde vergi incelemesine ek olarak teftiş, idari soruşturma, TPKK, suç gelirlerinin aklanması mevzuatı ve araştırma görevleri de bulunur. Sistem bunların varlığını tanır fakat alan mevzuatı ve gerçek görevlendirme olmadan bu yetkileri taklit etmez.

## 3. Vergi incelemesi modları

### `taxpayer_readiness`

Mükellef, SMMM veya YMM'nin inceleme öncesi dosyasını hazırlamak içindir. Görevlendirme ve başlama bildirimi zorunlu değildir. Sonuç `DRAFT_TAXPAYER_READINESS_ONLY` olur.

### `authorized_inspector_support`

Yalnızca gerçek yetkili kullanıcının analitik çalışmasına destek içindir. Aşağıdakiler yoksa motor `BLOCK` verir:

- yetki/görevlendirme kanıtı,
- görev referansı,
- kapsam ve başlama bildirimi,
- başlama bildiriminin dosya referansı.

Eklenti bu modda da kimlik ibrazı, resmî talep, arama, tutanak imzası veya rapor düzenleme yetkisi kullanmaz. Sonuç `DRAFT_FOR_AUTHORIZED_INSPECTOR` olur.

## 4. Mevzuattan çıkarılan YMM yetenekleri

3568 sayılı Kanunun 2/B, 11 ve 12 nci maddeleri ile ilgili yönetmelikler şu kapılara dönüştürülmüştür:

- YMM ruhsatı, çalışanlar listesi ve mühür kontrolü.
- Bağımsızlık, tarafsızlık, dürüstlük ve mesleki özen.
- Tasdiğe engel yakınlık ve ilişki kontrolü.
- YMM tasdik görevi ile defter tutma/muhasebe bürosu faaliyetinin ayrılması.
- Yazılı denetim/tasdik sözleşmesi ve tasdik ilişkisinin açık yazılması.
- İşletmeyi tanıma, önemlilik, risk ve denetim planı.
- Defter-belge, mali tablo ve beyanname mutabakatı.
- Yeterli ve güvenilir kanıt.
- Örnekleme ve karşıt inceleme izi.
- Maddi bulguların giderilmesi veya rapor etkisine açıkça taşınması.
- Rapor kapsamının ve kanuni sorumluluk alanının açık yazılması.
- Tasdik türüne özgü güncel tebliğ, had, süre ve rapor formatı kontrolü.

Motor tam tasdik, KDV iadesi, istisna, iade, indirim, tecil/terkin, zarar mahsubu ve özel amaçlı tasdik türlerini sınıflandırır. Ancak değişken had ve oranları katalogda sabit tutmaz; tarihli resmî kaynak girdisi ister.

## 5. YMM modları

### `pre_certification_readiness`

Mükellef veya SMMM'nin YMM'ye teslim edeceği dosyayı hazırlamak içindir. Ruhsat, liste ve mühür bu hazırlık modunda zorunlu değildir. Sonuç `DRAFT_READINESS_ONLY` olur.

### `licensed_ymm_support`

Gerçek YMM çalışma dosyası içindir. Ruhsat, ruhsat kanıt referansı, çalışanlar listesi ve mühür kontrolü eksikse `BLOCK` verir. Sonuç `DRAFT_FOR_LICENSED_YMM` olur; tasdik veya imza sonucu olmaz.

## 6. Deterministik Python rol motoru

Motor dosyası:

```text
skills/muhasebecim/scripts/professional_role_engine.py
```

Kural kataloğu:

```text
skills/muhasebecim/scripts/data/professional_roles.v1.json
```

Katalog 17 mevzuat kaynağına bağlı 48 kural içerir. Kural kimlikleri `VI-...` ve `YMM-...` öneklerini kullanır.

Motorun üç işlemi vardır:

```powershell
python .\skills\muhasebecim\scripts\professional_role_engine.py catalog-audit

python .\skills\muhasebecim\scripts\professional_role_engine.py `
  inspection-readiness-validate --example --output .\inspection-readiness.json

python .\skills\muhasebecim\scripts\professional_role_engine.py `
  ymm-certification-validate --example --output .\ymm-certification.json
```

Örneği düzenledikten sonra sonucu üretin:

```powershell
python .\skills\muhasebecim\scripts\professional_role_engine.py `
  inspection-readiness-validate `
  --input .\inspection-readiness.json `
  --output .\inspection-readiness-result.json
```

## 7. Sonuç nasıl okunur?

| Alan | Anlamı |
|---|---|
| `decision` | `PASS`, `PASS_WITH_WARNINGS`, `BLOCK` veya `ERROR` |
| `findings` | Kural kimliği, seviye, alan, açıklama, kaynak ve fiilî değer |
| `evaluated_rule_ids` | Girdiye gerçekten uygulanan kurallar |
| `catalog.sha256` | Kullanılan rol kataloğunun özeti |
| `input_sha256` | Girdinin kanonik özeti |
| `receipt_sha256` | Sonuçta sonradan değişiklik olup olmadığını kontrol eden makbuz |
| `output_status` | Sonucun hangi taslak statüsünde olduğu |
| `professional_act_permitted` | Her zaman `false`; yazılım resmî mesleki işlem yapamaz |

Çıkış kodu `0` geçiş, `1` iş kuralı bloku ve `2` şema/katalog/sistem hatasıdır.

## 8. Vaka kapanışına bağlama

Her üç rolde de [Mükellef Menfaati ve İç Bildirim Rehberi](MUKELLEF-MENFAATI-VE-IC-BILDIRIM.md) uygulanır. Lehe adım hazırlanır; aleyhe husus yerel iç kayıtta kullanıcı/SMMM/YMM'ye gösterilir. Yetkili müfettiş modunda lehe ve aleyhe kanıt birlikte değerlendirilir; YMM modunda bağımsızlık ve doğru raporlama korunur.

Her vaka için zorunlu sonuç yolu:

```text
outputs/taxpayer-interest-result.json
```

Bu kapı fiziksel lehe adım/iç bildirim dosyasını, SHA-256 bağını, görülme kaydını ve motor makbuzunu doğrular. `case.json` içinden kapatılamaz.

Vergi incelemesi hazırlığı gereken vakada `case.json`:

```json
{
  "requires_inspection_readiness": true
}
```

Sonuç yolu:

```text
outputs/inspection-readiness-result.json
```

YMM dosyası gereken vakada:

```json
{
  "requires_ymm_certification": true
}
```

Sonuç yolu:

```text
outputs/ymm-certification-result.json
```

`case_workflow.py`, motor adını, işlem türünü, kararı, `professional_act_permitted: false` sınırını ve SHA-256 makbuzunu birlikte doğrular. Sonuç elle değiştirilirse vaka kapısı kapanır.

## 9. Mevzuat ingest'i

Rol kaynaklarını yerel korpusa alın:

```powershell
python .\skills\muhasebecim\scripts\ingest_sources.py ingest `
  --manifest .\manifests\professional-roles-sources.json `
  --corpus .\corpus\official
```

Manifest VUK, 3568 sayılı Kanun, vergi inceleme yönetmeliği, VDK hak/yükümlülük sayfaları, 2026 işlenmiş meslek yönetmeliği, YMM Tasdik Yönetmeliği ve 27 Sıra No.lu Tebliği içerir.

## 10. Kritik mevzuat uyarısı

HMB'deki işlenmiş vergi inceleme yönetmeliği PDF'i 7 Nisan 2021'e kadar değişiklik işaretleri taşır. Sonraki VUK değişikliği nedeniyle inceleme yeri konusunda eski PDF ile güncel konsolide VUK 139 farklı ifade içerir. Motor eski “işyeri esastır” kuralını kodlamaz; işlem tarihinde güncel VUK'un yeniden doğrulanmasını zorunlu tutar.

Benzer şekilde YMM tasdik konularındaki parasal had, istisna, rapor formatı ve süreler zamanla değişebildiği için motor bunları sabit kodlamaz.

## 11. Sistem neyi başaramaz?

- Vergi müfettişi veya YMM unvanı vermez.
- Kamu yetkisi, arama, resmî ibraz talebi veya tutanak imzası kullanmaz.
- Vergi suçu veya sahte belge hakkında nihai hukuki sonuç vermez.
- YMM raporunu imzalamaz, mühürlemez veya idareye sunmaz.
- Kanuni müşterek/müteselsil sorumluluğu üstlenmez.
- Eksik veriyi veya güncel mevzuat doğrulamasını model tahminiyle tamamlamaz.

## 12. Gerçek veri testinden önce

1. Veriyi `cases/` altında tutun; GitHub'a eklemeyin.
2. VKN/TCKN, ad, banka hesabı ve personel bilgisini gereksiz çıktılarda maskeleyin.
3. İşlem tarihi ve incelenecek dönemi kesinleştirin.
4. Güncel mevzuat kaynaklarını ingest edin.
5. Hazırlık veya yetkili destek modunu doğru seçin.
6. Motor örneklerini vaka bilgileriyle doldurun.
7. Hukuka uygun lehe adımı ve aleyhe husus varsa yerel iç bildirimi fiziksel çalışma kâğıdı olarak hazırlayın.
8. `taxpayer_interest_engine.py` sonucunu üretip `outputs/taxpayer-interest-result.json` yoluna yazın.
9. `BLOCK` bulgularını kapatmadan `finalize` yapmayın.
10. Dış sunumdan önce ruhsatlı/yetkili meslek mensubu incelemesini tamamlayın.
