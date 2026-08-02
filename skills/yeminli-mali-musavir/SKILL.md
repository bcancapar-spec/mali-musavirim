---
name: yeminli-mali-musavir
description: Yeminli mali müşavirlik ve YMM tasdik dosyaları için iş kabulü, ruhsat/çalışma listesi, yazılı sözleşme, bağımsızlık ve akrabalık engeli, defter tutma yasağı, denetim planı, yeterli ve güvenilir kanıt, karşıt inceleme, tam tasdik, KDV iadesi ve diğer tasdik raporu kalite kapılarında kullan. Tüm hesaplama ve mutabakatı yerelde çalıştırılan Python koduyla yapar. İmza, mühür ve tasdik yetkisini üstlenmez.
---

# Yeminli Mali Müşavir Tasdik Desteği

## Yetki ve bağımsızlık kapısı

Bu yetenek iki modda çalışır:

- `pre_certification_readiness`: mükellef/SMMM için tasdik öncesi dosya hazırlığı; sonuç daima taslaktır.
- `licensed_ymm_support`: ruhsat, çalışanlar listesi ve mühür kanıtı bulunan gerçek YMM'nin çalışma dosyasına analitik destek.

Sanal yardımcı YMM değildir; tasdik raporu imzalayamaz, mühürleyemez, idareye sunamaz veya müşterek/müteselsil sorumluluğu üstlenemez. YMM'nin kanunen yasaklanan defter tutma ve muhasebe bürosuna ortak olma faaliyetini tasdik işiyle birleştirme.

Mevzuat haritası için [mevzuat-ve-yetki.md](references/mevzuat-ve-yetki.md), dosya akışı için [tasdik-is-akisi.md](references/tasdik-is-akisi.md) dosyasını oku.

Her vakada `../muhasebecim/references/taxpayer-interest-policy.md` ortak politikasını uygula. Hukuka uygun mükellef lehine düzeltme, kanıt tamamlama, açıklama veya başvuru adımını hazırla. Aleyhe hususu kullanıcı/YMM'ye yerel iç bildirimle eksiksiz göster ve görülme kaydı al. Giderilemeyen hususu rapor etkisi, kapsam sınırlaması, iş kabulü veya çekilme değerlendirmesinden saklama; bağımsızlık ve doğru raporlama “mükellef lehine” gerekçesiyle kaldırılamaz.

## Zorunlu tasdik döngüsü

1. Tasdik türünü, dönemi, vergi türünü, hukuki dayanağı, güncel tebliğ/rapor formatını ve teslim tarihini belirle.
2. `licensed_ymm_support` modunda ruhsat, çalışanlar listesi, mühür ve yetki kanıtı olmadan devam etme.
3. Bağımsızlık, tarafsızlık, çıkar çatışması, yakınlık/ilişki engeli ve defter tutma ayrımını belgele. Engel varsa `BLOCK`.
4. Yazılı sözleşmede taraflar, konu/kapsam, tablolar, dönem, yer, insan-saat, başlama/bitiş, rapor tarihi ve işin tasdikle ilişkisini açıkça yaz.
5. Önemlilik, risk, denetim planı ve örneklem yöntemini belgeye bağla.
6. Defter, belge, finansal tablo ve beyannameleri mutabıklaştır. Her sayıyı Python hesap iziyle yeniden üret.
7. Yeterli ve güvenilir kanıt elde et. Karşıt inceleme gereken/aranmayan işlemleri güncel tebliğ zinciriyle belirle; yapılamayan prosedürün etkisini sınırla veya rapora taşı.
8. Her bulguyu `olgu -> mevzuat -> prosedür -> kanıt -> Python hesabı -> müşteri açıklaması -> sonuç` zincirinde kur.
9. Raporun tasdik kapsamını açık yaz; kapsam dışı işlem için güvence verme. Değişken parasal had, oran, form ve süreyi sabit kodlama.
10. Raporu ruhsatlı YMM'nin mesleki incelemesine sun; sistem sonucu yalnızca `DRAFT_FOR_LICENSED_YMM` veya `DRAFT_READINESS_ONLY` olabilir.
11. Lehe adım ve aleyhe iç bildirim dosyalarını SHA-256 ile bağla; `taxpayer_interest_engine.py` sonucu geçmeden dosyayı kapanışa gönderme.

## Python ve yerel veri zorunluluğu

Müşteri verisini yalnızca yerelde işle. Tutar, oran, tarih/süre, sıralama, örnekleme, mutabakat ve veri dönüşümünü Python 3.11+ ile çalıştır. Parasal değerlerde `Decimal`; denetim izinde SHA-256 kullan. Uzak OCR, LLM veya analiz hizmetine müşteri belgesi yükleme.

Deterministik tasdik kapısını çalıştır:

```powershell
python ..\muhasebecim\scripts\professional_role_engine.py ymm-certification-validate `
  --input ymm-certification.json --output ymm-certification-result.json

python ..\muhasebecim\scripts\taxpayer_interest_engine.py taxpayer-interest-validate `
  --input taxpayer-interest.json --output taxpayer-interest-result.json
```

`PASS`, tasdik yapıldığı anlamına gelmez; yalnızca tanımlı dosya kapılarının geçtiğini gösterir.
