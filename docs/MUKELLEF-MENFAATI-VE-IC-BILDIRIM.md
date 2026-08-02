# Mükellef Menfaati ve İç Bildirim — v0.0.3 Mali Müşavir Rehberi

## Kısa sonuç

v0.0.3 ile her vaka için yeni ve kapatılamayan bir kontrol eklenmiştir:

1. En az bir hukuka uygun, hazırlanmış ve süresi geçmemiş mükellef lehine adım bulunacak.
2. Aleyhe her husus kullanıcı, SMMM veya YMM için yerel iç risk kaydına dönüşecek.
3. İç kayıt görülüp kabul edilmeden vaka kapanmayacak.
4. Lehe adım ve iç bildirim dosyaları fiziksel dosya yolu ile SHA-256 özetine bağlanacak.
5. Aleyhe olgu gizleme, hukuka aykırı yöntem, tarafsızlık/bağımsızlık kaybı veya otomatik dış iletim varsa motor `BLOCK` verecek.

Bu kayıt vergi dairesine, müşteriye veya üçüncü kişiye otomatik gönderilmez. Meslek mensubunun karar vermesi için yerel “iç istihbarat” çalışma kâğıdıdır.

## Mükellef lehine adım örnekleri

| Durum | Hazırlanabilecek hukuka uygun adım |
|---|---|
| Belge eksik | Dayanak belgenin tamamlanması ve açıklama dosyası |
| Kayıt hatası | Doğru düzeltme kaydı ve beyan etkisi hesabı |
| Vergi farkı riski | İzah, düzeltme, uzlaşma, itiraz veya dava seçeneğinin süreli değerlendirmesi |
| Tevsik sorunu | Alternatif geçerli kanıt ve karşı taraf teyidi |
| İnceleme süreci | Kapsam, hak, tebligat, süre ve tutanak mülahazası kontrolü |
| Ödeme güçlüğü | Mevzuatta mevcut ödeme/tecil/taksit seçeneğinin tarihli hesabı |

Motor tek başına hangi seçeneğin doğru olduğuna hukuki garanti vermez. Seçenek vaka tarihindeki resmî mevzuata ve gerçek kanıta bağlanır.

## Aleyhe husus nasıl kaydedilir?

Örnek yerel iç bildirim dosyası:

```json
{
  "matter_id": "RISK-001",
  "severity": "high",
  "summary": "Belge ile kayıt arasında açıklanması gereken fark var.",
  "factual_basis_references": ["workpapers/reconciliation.json"],
  "legal_basis_reference": "Vaka tarihinde doğrulanan VUK hükümleri",
  "protective_action_id": "ACTION-001",
  "recipients": ["user", "smmm"],
  "acknowledged_by": "SMMM-MASKED",
  "acknowledged_at": "2026-08-02",
  "external_transmission": false
}
```

Tutar etkisi varsa zihinden yazılmaz. Ayrı Python hesabı çalıştırılır ve `estimated_impact_reference` alanına sonuç dosyası bağlanır.

## Motoru çalıştırma

```powershell
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py catalog-audit

python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py `
  taxpayer-interest-validate --example `
  --output .\taxpayer-interest.json

python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py `
  taxpayer-interest-validate `
  --input .\taxpayer-interest.json `
  --output .\cases\ornek\outputs\taxpayer-interest-result.json
```

Lehe adım veya iç bildirim dosyasının SHA-256 özetini Python ile hesaplayın:

```powershell
python -c "from pathlib import Path; import hashlib; p=Path(r'.\cases\ornek\workpapers\taxpayer-actions\ACTION-001.json'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Bu özeti motor girdisindeki ilgili `action_sha256` veya `alert_sha256` alanına yazın. Ardından motoru yeniden çalıştırın.

## Sonuç alanları

| Alan | Mali müşavir için anlamı |
|---|---|
| `decision` | `PASS`, `PASS_WITH_WARNINGS`, `BLOCK` veya `ERROR` |
| `taxpayer_favorable_path_status` | Güncel ve hazırlanmış lehe adım varsa `PREPARED` |
| `internal_intelligence_status` | Aleyhe husus yoksa `CLEAR`; tamamı görüldüyse `ACKNOWLEDGED` |
| `active_favorable_action_records` | Lehe adım dosyası ve SHA-256 bağı |
| `internal_alert_records` | Aleyhe iç bildirim dosyası ve SHA-256 bağı |
| `external_transmission_permitted` | Her zaman `false` |
| `professional_act_permitted` | Her zaman `false` |
| `receipt_sha256` | Motor sonucunun sonradan değiştirilip değiştirilmediğini gösteren makbuz |

## Rol farkları

- **SMMM/mükellef hazırlığı:** Mükellefin hakkını en iyi koruyan doğru kayıt, kanıt, düzeltme ve başvuru adımı hazırlanır.
- **Vergi müfettişi desteği:** Lehe ve aleyhe kanıt birlikte ele alınır; mükellef hakları ve lehe düzeltmeler dosyaya girer. Aleyhe bulgu bastırılmaz.
- **YMM desteği:** Önce düzeltme seçeneği hazırlanır. Giderilemeyen maddi husus rapor etkisine, kapsam sınırlamasına veya iş kabul/çekilme kararına taşınır. Bağımsızlık bozulmaz.

## Nelerin yapılması yasaktır?

- Gerçeğe aykırı kayıt veya beyan üretmek.
- Aleyhe belgeyi silmek, değiştirmek veya iç analizden saklamak.
- Zorunlu açıklamayı “mükellef lehine” gerekçesiyle atlamak.
- Vergi müfettişi veya YMM modunda tarafsızlık/bağımsızlığı kaldırmak.
- İç risk kaydını kendiliğinden e-posta, bulut, idare veya üçüncü kişiye göndermek.
- İnsan incelemesi olmadan beyan, imza, tasdik veya resmî işlem yapmak.

## Vaka kapanışı

`case_workflow.py finalize`, `outputs/taxpayer-interest-result.json` bulunmadan artık hiçbir vakayı `ready_for_professional_review` durumuna getirmez. `case.json` içindeki alanı `false` yapmak bu kontrolü kapatmaz. Dosya eksikse, UTF-8 JSON içindeki kimlik motor sonucuyla eşleşmezse, hash tutmazsa, iç bildirim görülmemişse veya lehe adım süresi geçmişse kapı kapanır.
