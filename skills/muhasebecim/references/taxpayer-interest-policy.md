# Mükellef menfaati ve zorunlu iç bildirim politikası

Bu dosya, eklentideki üç yeteneğin ortak ve tek yetkili politika kaynağıdır. Her muhasebe, vergi incelemesi hazırlığı ve YMM tasdik vakasında uygulanır.

## 1. Ana ilke

Sistem, mevcut olgular ve vaka tarihinde doğrulanan mevzuat içinde mükellefin hak ve menfaatini en iyi koruyan uygulanabilir adımı hazırlar. “Mükellef lehine” şu tür hukuka uygun işlerdir:

- hakkın ve usul güvencesinin kullanılması,
- eksik kanıtın tamamlanması ve mükellef açıklamasının belgelenmesi,
- doğru kayıt veya beyannamenin süresinde düzeltilmesi,
- izah, uzlaşma, itiraz, dava/kanun yolu veya ödeme planı seçeneğinin hazırlanması,
- süre, tebligat, kapsam, yetki ve ispat külfeti kontrolleri,
- gereksiz ikrar veya karşı tarafa/idareye gereksiz koz veren anlatımdan kaçınma.

Lehe hazırlık hiçbir zaman kayıt dışılık, yanıltıcı belge, gerçeğe aykırı beyan, kanıt gizleme/yok etme, zorunlu açıklamayı atlama veya bağımsızlık ihlali anlamına gelmez.

## 2. İç dürüstlük ve dış koruma ayrımı

İki katman birbirine karıştırılmaz:

1. **Yerel iç çalışma kaydı:** Aleyhe olgular, kanıtlar, mevzuat, tutarsızlıklar, süre riskleri ve olası etkiler eksiksiz kaydedilir. Gizlenmez, küçültülmez ve silinmez. Kullanıcı veya yetkili SMMM/YMM mutlaka bilgilendirilir.
2. **Dış taslak:** Mükellefi gereksiz yere zayıflatan, zorunlu olmayan ikrar veya karşı tarafı/idareyi gereksiz yere silahlandıran ifade üretilmez. Buna karşılık kanunen verilmesi gereken bilgi, doğru muhasebe kaydı, beyan, tasdik kapsamı veya resmî inceleme bulgusu saklanamaz. Dış taslak daima insan ve yetki incelemesine tabidir.

Bu yaklaşım, `ortak-avukat` projesindeki “iç analizde zaafı saklamama, dış metinde müvekkili gereksiz zayıflatmama” ayrımından yöntem düzeyinde ilham alır. Muhasebe ve vergi uygulaması için bağımsız olarak kodlanmıştır; diğer projenin metni veya kaynak kodu kopyalanmaz.

## 3. “İç istihbarat” ne demektir?

İç istihbarat, gizli veya yetkisiz veri toplama değildir. Yalnızca kullanıcının sağladığı ya da işlemeye yetkili olduğu vaka verilerinden üretilen **yerel iç risk ve karar kaydıdır**. Otomatik olarak e-posta, bulut, idare veya üçüncü kişiye gönderilmez.

Her aleyhe husus kaydı en az şunları içerir:

- benzersiz husus kimliği ve nitel önem seviyesi,
- kısa ve tarafsız özet,
- olgusal/kanıtsal dayanak dosyaları,
- vaka tarihinde doğrulanan hukuki dayanak,
- varsa ayrı Python hesabına bağlanan etki referansı,
- uygulanabilir mükellef koruma adımının kimliği,
- kullanıcı/SMMM/YMM alıcısı,
- “görüldü” kaydı, gören kişi ve tarih,
- yerel dosya yolu ve dosyanın SHA-256 özeti,
- `external_transmission: false` kilidi.

## 4. Rol bazlı sınırlar

### Mali müşavirlik ve mükellef hazırlığı

Önce hukuka uygun en yararlı düzeltme, kanıt, açıklama veya hak kullanım adımı hazırlanır. Aleyhe husus iç kayda alınır ve kullanıcı/meslek mensubu bilgilendirilir. Beyan ve defter doğruluğu bozulamaz.

### Yetkili vergi müfettişi desteği

VUK 134 kapsamındaki doğruluk amacı ile lehe ve aleyhe kanıtın birlikte değerlendirilmesi esastır. “Lehe adım”, mükellef haklarının, açıklamalarının, düzeltme gerektiren lehe sonuçların ve usul güvencelerinin dosyaya alınmasıdır; aleyhe bulguyu bastırmak değildir. Yetki ve tarafsızlık kapıları korunur.

### YMM tasdik desteği

Bağımsızlık, tarafsızlık, yeterli/güvenilir kanıt ve doğru raporlama korunur. Aleyhe husus kullanıcı/YMM'ye bildirilir; mümkünse düzeltme hazırlanır. Giderilemeyen maddi husus kapsam sınırlaması, görüş/rapor etkisi, işin kabul edilmemesi veya çekilme değerlendirmesine taşınır; gizlenmez.

## 5. Deterministik motor

Katalog ve motor:

```text
scripts/data/taxpayer_interest_rules.v1.json
scripts/taxpayer_interest_engine.py
```

Örnek girdi ve kontrol:

```powershell
python scripts/taxpayer_interest_engine.py catalog-audit
python scripts/taxpayer_interest_engine.py taxpayer-interest-validate --example --output taxpayer-interest.json
python scripts/taxpayer_interest_engine.py taxpayer-interest-validate `
  --input taxpayer-interest.json --output taxpayer-interest-result.json
```

Motorun kapalı rol modları:

- `accountant_advisory`
- `taxpayer_readiness`
- `authorized_inspector_support`
- `pre_certification_readiness`
- `licensed_ymm_support`

Lehe adım türleri `right_assertion`, `evidence_completion`, `voluntary_correction`, `reconciliation`, `explanation`, `objection`, `settlement`, `appeal`, `payment_or_installment` ve `other` değerlerinden biridir.

## 6. Fiziksel kanıt ve vaka kapısı

Modelin “hazırladım” demesi yeterli değildir. Her aktif lehe adım `action_reference` ve `action_sha256`; her aleyhe bildirim `alert_reference` ve `alert_sha256` ile fiziksel dosyaya bağlanır. `case_workflow.py`:

- referansın vaka dizini dışına çıkmadığını,
- dosyanın gerçekten var olduğunu ve UTF-8 JSON içindeki `action_id`/`matter_id` değerinin sonuçla eşleştiğini,
- dosya baytlarının SHA-256 değerinin motor sonucuyla eşleştiğini,
- sonuç makbuzunun değiştirilmediğini,
- lehe adım durumunun `PREPARED` olduğunu,
- aleyhe husus varsa iç bildirim durumunun `ACKNOWLEDGED` olduğunu

doğrular. Bu kapı tüm vakalarda zorunludur ve `case.json` değiştirilerek kapatılamaz.

Motor sonucunu vaka içinde şu yola yaz:

```text
outputs/taxpayer-interest-result.json
```

Lehe adım dosyalarını `workpapers/taxpayer-actions/`, aleyhe iç bildirimleri `workpapers/internal-intelligence/` altında tut. Gerçek müşteri verilerini GitHub'a ekleme.

## 7. Son karar ve dış iletim

Motor çıktısı `INTERNAL_TAXPAYER_PROTECTION_RECORD` statüsündedir. `external_transmission_permitted` ve `professional_act_permitted` her zaman `false` kalır. Dış gönderim, beyan, imza, mühür, tasdik veya resmî işlem yalnızca yetkili insan kararıyla yapılır.
