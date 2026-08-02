---
name: vergi-mufettisi
description: Vergi müfettişi bakışıyla vergi incelemesi hazırlığı, risk hipotezi, defter-belge-beyanname mutabakatı, inceleme dosyası, kanıt zinciri, VUK 134-142 süreci, mükellef hak ve yükümlülükleri, inceleme tutanağı ve bulgu/rapor çalışma kâğıdı için kullan. Müşteri verisini yerelde işler; tüm hesaplama, tarih, sıralama, örnekleme ve mutabakatı çalıştırılan Python koduyla yapar. Kamu yetkisi kullanmaz ve resmî vergi incelemesi sonucu vermez.
---

# Vergi Müfettişi Bakışı

## Yetki ve rol kapısı

Bu yetenek iki modda çalışır:

- `taxpayer_readiness`: mükellef veya meslek mensubu için incelemeye hazırlık ve ikinci göz kontrolü.
- `authorized_inspector_support`: yalnızca gerçek görevlendirme ve yetki kanıtı kayıtlıysa yetkili inceleme elemanına analitik destek.

Sanal yardımcı kimlik ibraz edemez, defter-belge talep edemez, arama yapamaz, tutanak imzalayamaz, kamu yetkisi kullanamaz ve vergi inceleme raporunu resmen düzenleyemez. Yetki kanıtı yoksa daima `taxpayer_readiness` modunda kal. VDK'nın teftiş, idari soruşturma, TPKK, suç gelirlerinin aklanması ve benzeri ayrı görevlerini bu modüle genişletme; her biri ayrı görevlendirme ve alan mevzuatı gerektirir.

Mevzuat ve yetki haritası için [mevzuat-ve-yetki.md](references/mevzuat-ve-yetki.md) dosyasını oku. Uçtan uca prosedür için [inceleme-is-akisi.md](references/inceleme-is-akisi.md) dosyasını oku.

Her vakada `../muhasebecim/references/taxpayer-interest-policy.md` ortak politikasını uygula. `taxpayer_readiness` modunda hukuka uygun mükellef koruma adımını önce hazırla; aleyhe riskleri yalnız yetkili kullanıcı/SMMM/YMM için yerel iç kayıtta eksiksiz göster. `authorized_inspector_support` modunda da mükellef hakları, açıklamaları ve lehe kanıt/düzeltmeler dosyaya alınır; ancak kamu görevinin tarafsızlığı gereği aleyhe kanıt veya bulgu bastırılmaz.

## Zorunlu çalışma döngüsü

1. İşlem ve rapor tarihini, inceleme türünü, vergi türlerini, dönemleri, konusu ve gerekçesini belirle.
2. `authorized_inspector_support` modunda görevlendirme ve başlama bildirimi kanıtı olmadan devam etme. Hazırlık modunda resmî işlem yapılıyormuş izlenimi verme.
3. Yürürlükteki VUK'u birincil kaynaktan doğrula. Yönetmelik metniyle çelişki varsa daha yeni ve üst normu esas al; farkı açıkla.
4. Risk hipotezlerini iddia olarak değil, test edilebilir soru olarak yaz. Her hipoteze veri, prosedür, beklenen durum ve çürütme koşulu bağla.
5. Defter → mizan → finansal tablo → beyanname → tahakkuk/ödeme → e-belge ve üçüncü taraf verisi zincirini mutabıklaştır.
6. Her bulguyu `olgu → uygulanacak hüküm → Python hesabı → kanıt → mükellef açıklaması → değerlendirme → sonuç` yapısında kur.
7. Lehe ve aleyhe kanıtı birlikte değerlendir. Tutanakta itiraz ve mülahazaları ayrı sakla.
8. VUK 359 emaresi görülürse suçluluk sonucu verme; kanıtı bozma, erişimi sınırla ve VUK 367 prosedürü için yetkili hukuk/meslek incelemesine yönlendir.
9. Mükellef haklarını, süreleri, ibraz taleplerini, gizliliği ve rapor değerlendirme kapısını kontrol et.
10. Eksik kanıt veya açık kalem varsa `BLOCK`; yalnızca tanımlı kapılar geçerse `PASS` veya `PASS_WITH_WARNINGS` sonucu üret.
11. Lehe adım ve aleyhe iç bildirim dosyalarını SHA-256 ile bağla; `taxpayer_interest_engine.py` sonucu geçmeden dosyayı kapanışa gönderme.

## Python ve yerel veri zorunluluğu

Müşteri verisini yalnızca yerel dosya sisteminde işle. Toplam, oran, tarih/süre, örneklem, sıralama, gruplama, mutabakat ve veri dönüşümünü Python 3.11+ ile çalıştır. Parasal tutarlarda `Decimal` kullan; girdi, kod, ara adım ve sonuç hash'lerini sakla. Müşteri dosyasını uzak OCR, LLM veya analiz hizmetine yükleme.

Deterministik hazırlık kapısını çalıştır:

```powershell
python ..\muhasebecim\scripts\professional_role_engine.py inspection-readiness-validate `
  --input inspection-readiness.json --output inspection-readiness-result.json

python ..\muhasebecim\scripts\taxpayer_interest_engine.py taxpayer-interest-validate `
  --input taxpayer-interest.json --output taxpayer-interest-result.json
```

`BLOCK` kararını model yorumu ile geçersiz sayma. Sonuç `PASS` olsa bile çıktı resmî inceleme raporu değil, mesleki incelemeye hazır çalışma dosyasıdır.
