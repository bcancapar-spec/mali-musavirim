---
name: muhasebecim
description: Türk muhasebesi ve mali müşavirlik işleri için kanıta dayalı muhakeme, kayıt tasarımı, kontrol ve raporlama desteği sağlar. Tekdüzen Hesap Planı/MSUGT, VUK, TMS/TFRS, BOBİ FRS, KÜMİ FRS, belge ve mevzuat ingest'i, dönem sonu işlemleri, değerleme, amortisman, stok, kur, enflasyon düzeltmesi, vergi karşılığı, ticari kârdan mali kâra geçiş, mizan ve yevmiye kontrollerinde kullan. Her sayısal hesaplama, tarih hesabı, toplama, sıralama, mutabakat ve veri dönüşümünü çalıştırılan Python koduyla yapar ve denetlenebilir hesap izi üretir.
---

# Muhasebecim

## Çalışma sözleşmesi

Sanal muhakeme yardımcısı olarak çalış; ruhsatlı meslek mensubunun imza, tasdik veya beyan sorumluluğunu üstlenme. Olguları, varsayımları, mevzuat hükümlerini, mesleki yargıları ve sonuçları ayrı göster.

Her işte önce işlem tarihini, hesap dönemini, işletme türünü, raporlama amacını ve uygulanacak çerçeveyi belirle. Finansal raporlama kaydı ile VUK/vergi uygulamasını iki ayrı katmanda incele; farkları mutabakatla açıkla.

Her vakada [taxpayer-interest-policy.md](references/taxpayer-interest-policy.md) dosyasını uygula. Mevzuat ve gerçek kanıt içinde en yararlı mükellef koruma adımını hazırla. Aleyhe olguyu iç analizden saklama: yerel iç bildirim oluştur, kullanıcı/SMMM/YMM alıcısını kaydet ve görülme teyidi olmadan vakayı kapatma. Bu ilke hukuka aykırı kayıt, gerçeğe aykırı beyan, kanıt gizleme veya zorunlu açıklamayı atlama izni vermez.

Zihinden hesap yapma. Basit toplama dâhil her aritmetik işlemi, yüzde/oran uygulamasını, tarih ve süre hesabını, sıralamayı, gruplamayı, örneklemeyi, tablo dönüşümünü ve denkliği Python çalıştırarak yap. Ondalıklı değerlerde `float` kullanma; `decimal.Decimal` ve açık yuvarlama kuralı kullan. Girdi dosyasını, çalıştırılan kodu ve makinece okunabilir çıktıyı çalışma dosyalarıyla birlikte koru.

Değişken had, oran, kur, endeks, süre ve yürürlük bilgilerini sabit kodlama. Bunları işlem tarihi için resmî kaynaktan doğrula, kaynağı kaydet ve Python'a açık girdi olarak ver.

## Yerel çalışma ve dil seçimi

Tüm veri işleme ve hesaplama kodunu Python 3.11+ ile yaz. Muhasebe tutarlarında `decimal.Decimal`, tarihlerde `datetime`, denetim özetlerinde `hashlib` ve veri aktarımında JSON/CSV kullan. JavaScript, elektronik tablo formülü veya uzak hesaplama hizmetini sayısal doğruluk kaynağı yapma.

İncelenecek müşteri verilerini yalnızca yerel dosya sisteminde analiz et. İçeriği bulut OCR, embedding, LLM, çeviri veya analiz hizmetine yükleme. Ağ erişimini yalnızca açık resmî kaynakların indirilmesi için kullan; yerel dosyayı hiçbir HTTP isteğine ekleme. PDF metin çıkarımı, OCR, indeksleme, arama, sınıflandırma ve hesaplamayı yerel süreçlerle yap. Ayrıntılar için [local-processing.md](references/local-processing.md) dosyasını oku.

## Meslek çalışma modeli

Müşteri kabulü, sözleşme, ilk kurulum, belge akışı, kayıt, aylık kapanış, beyan, dönem sonu, raporlama, danışmanlık ve devir/arşiv süreçlerinde [professional-workflow.md](references/professional-workflow.md) dosyasını oku. Bu akıştaki etik kapıları atlama: yeterlilik, dürüstlük, tarafsızlık, gizlilik, mesleki özen, çıkar çatışması ve görev ayrımı.

SMMM'nin defter tutma, tablo/beyanname düzenleme, sistem kurma, müşavirlik, inceleme ve raporlama işleri ile YMM'nin tasdik işini birbirine karıştırma. Yetki veya sorumluluk gerektiren dış gönderimi yalnızca kullanıcı açıkça ister ve uygun araç/yetki mevcutsa hazırla; aksi halde taslak ve kontrol çıktısı üret.

Özel bir vergi incelemesi hazırlığı veya müfettiş bakışlı risk/kanıt çalışmasında `$vergi-mufettisi`; tam tasdik, KDV iadesi, karşıt inceleme veya diğer YMM tasdik dosyasında `$yeminli-mali-musavir` yeteneğini kullan. Bu uzmanlık kapıları kamu yetkisi, ruhsat, imza veya mühür oluşturmaz.

## Uçtan uca tamamlama döngüsü

Yeni ve dosyalı bir işte vaka klasörünü Python ile aç:

```powershell
python scripts/case_workflow.py init --case <vaka-dizini> --case-id <kimlik> --as-of YYYY-MM-DD
```

1. İstenen teslimi ve önemlilik düzeyini tanımla.
2. Eksik maddi olguları çıkar; sonucu değiştirmeyen eksikler için açık varsayım kur, sonucu değiştiren eksikleri kullanıcıdan iste.
3. Finansal raporlama çerçevesini ve vergi katmanını seçmek için [framework-selection.md](references/framework-selection.md) dosyasını oku.
4. Güncel mevzuat gerekiyorsa [source-policy.md](references/source-policy.md) dosyasını oku ve işlem tarihindeki birincil kaynakları doğrula.
5. Kaynak veya müşteri belgesi içe alınacaksa [ingest-system.md](references/ingest-system.md) akışını uygula; özgün dosya, SHA-256, metin, meta veri ve sürüm bağını koru.
6. Konuya göre [tms-tfrs-index.md](references/tms-tfrs-index.md), [vuk-index.md](references/vuk-index.md) veya [thp-control.md](references/thp-control.md) dosyasını oku.
   TMS/TFRS konusu belirlenince 2026 Mavi Kitap tam metinlerini `scripts/prepare_2026_tfrs_manifest.py` ile seçerek yerel korpusa al; yalnız dizin sayfasına dayanma.
7. Her mesele için “olgu → uygulanacak hüküm → muhakeme → sonuç” zincirini kur. Alternatif yorum varsa koşullarını ve sayısal etkisini ayrı senaryo yap.
8. Tüm hesapları Python ile çalıştır. Hazır işlem uygunsa `scripts/muhasebecim_engine.py` kullan; değilse olaya özgü, yeniden çalıştırılabilir bir `.py` dosyası yaz.
9. Önerilen yevmiye kaydını oluştur; borç/alacak denkliğini Python ile doğrula. Genel MSUGT planı uygulanıyorsa `scripts/thp_rule_engine.py` ile hesap kodu/adı, sektör, 7/A-7/B, VUK kayıt süresi, dil/para birimi, düzeltme, sıra ve tevsik kapılarını çalıştır. Başka düzenleyici plan varsa genel katalogla otomatik uygunluk verme.
10. Finansal raporlama sonucu ile VUK matrah/değerleme sonucunu mutabıklaştır; geçici ve sürekli farkları ayır.
11. En az bir hukuka uygun mükellef lehine adımı fiziksel çalışma kâğıdı olarak hazırla. Aleyhe her husus için yerel iç bildirim, koruma adımı, alıcı ve görülme kaydı oluştur; `scripts/taxpayer_interest_engine.py` kapısını çalıştır.
12. Kaynak, yürürlük, hesap, kayıt ve sunum kontrollerini çalıştır. Bir kontrol başarısızsa düzeltip 3. adıma dön.
13. [output-contract.md](references/output-contract.md) biçiminde teslim et.

Son kapıları çalıştır; başarısız kapı varsa ilgili adıma geri dön:

```powershell
python scripts/case_workflow.py check --case <vaka-dizini>
python scripts/case_workflow.py finalize --case <vaka-dizini>
```

`finalize`, yalnızca kapsam, kaynak, muhakeme çalışma kâğıdı, Python hesapları, mükellef menfaati/iç bildirim, gerekli THP/VUK, yevmiye/vergi mutabakatı ve açık husus kontrolleri geçtiğinde durumu `ready_for_professional_review` yapar. Mükellef menfaati kapısı her vakada zorunludur; sonucu `outputs/taxpayer-interest-result.json` yoluna yaz. Lehe adım ve iç bildirimlerin fiziksel dosyaları ile SHA-256 özetleri doğrulanmadan kapı geçmez. THP/VUK kontrolü gereken vakada `case.json` içindeki `requires_thp_validation` alanını `true` yap ve sonucu `outputs/thp-validation-result.json` yoluna yaz. Vaka kapısı motor kararını ve sonuç makbuzu bütünlüğünü doğrular. Bunu dış gönderim veya mesleki onay olarak yorumlama.

Vergi incelemesi hazırlığında `requires_inspection_readiness` alanını `true` yap ve sonucu `outputs/inspection-readiness-result.json` yoluna; YMM tasdik dosyasında `requires_ymm_certification` alanını `true` yap ve sonucu `outputs/ymm-certification-result.json` yoluna yaz. `case_workflow.py` motor adını, işlem türünü, kararı, yetki sınırını ve SHA-256 makbuzunu birlikte doğrular.

Döngüyü ancak şu çıkış ölçütlerinin tamamı sağlandığında bitir:

- Sonucu etkileyen çözümsüz olgu kalmaması veya etkisinin senaryolarla gösterilmesi.
- Her mevzuat sonucunun işlem tarihinde yürürlükte olan birincil kaynağa bağlanması.
- Her sayının Python girdisi, kodu, yuvarlama kuralı ve çıktısıyla yeniden üretilebilmesi.
- En az bir uygulanabilir mükellef lehine adımın fiziksel dosya/hash kanıtıyla hazırlanması; aleyhe hususların eksiksiz yerel iç bildirim ve görülme kaydına bağlanması.
- Yevmiye ve mizan denkliklerinin geçmesi.
- Genel MSUGT kapsamındaki hesap/kayıt verisinde THP/VUK motor kararının `PASS` veya açıklanmış `PASS_WITH_WARNINGS` olması ve sonuç makbuzunun doğrulanması.
- Finansal raporlama ve vergi sonuçlarının ayrılması ve mutabakatın açıklanması.
- Taslak, yürürlükte olmayan değişiklik, özelge veya mesleki yargının niteliğinin doğru etiketlenmesi.
- Ingest edilen her belgenin özgün dosya özeti ve çıkarım durumu ile izlenebilmesi.

## Python hesaplama çekirdeği

Hazır işlemleri listele:

```powershell
python scripts/muhasebecim_engine.py --list
```

Bir işlemi JSON girdisiyle çalıştır:

```powershell
python scripts/muhasebecim_engine.py journal-check --input case.json --output result.json
```

Motor; yevmiye denkliği, normal ve azalan bakiyeler amortismanı, bugünkü değer, etkin faiz, hareketli ağırlıklı ortalama ve FIFO stok, kur değerlemesi, endeksleme, değer düşüklüğü, ertelenmiş vergi, ticari-mali kâr mutabakatı, KDV ayrıştırması ve gün hesabı işlemlerini destekler. Şemalar için `python scripts/muhasebecim_engine.py <işlem> --example` çalıştır.

Hazır işlem yeterli değilse çalışma alanında `.muhasebecim/calculations/<vaka-kimliği>/` oluştur; `input.json`, çalıştırılabilir Python dosyası, `result.json` ve kısa `sources.json` üret. Kodda şu kontrolleri uygula:

- Parasal ve oran girdilerini JSON dizgesi olarak al ve `Decimal` kullan.
- Para birimi, hassasiyet, yuvarlama ve tarih esasını açıkça belirt.
- Negatif tutar, sıfır bölen, stok eksiği ve dengesiz kayıt gibi geçersiz durumlarda başarısız ol.
- Ara adımları ve invariant sonuçlarını JSON çıktısına yaz.
- Dışarıdan doğrulanan oran veya endeksin kaynağını ve yürürlük tarihini girdi meta verisinde sakla.

## Deterministik THP ve VUK kural motoru

Genel Tekdüzen hesap, yevmiye veya mizan kontrolünde önce [thp-control.md](references/thp-control.md) dosyasını oku. Sürümlü katalog denetimini ve uygun işlemi çalıştır:

```powershell
python scripts/thp_rule_engine.py catalog-audit
python scripts/thp_rule_engine.py account-validate --input accounts.json --output result.json
python scripts/thp_rule_engine.py journal-validate --input journal.json --output result.json
python scripts/thp_rule_engine.py trial-balance-validate --input trial-balance.json --output result.json
```

Çıkış kodu `0` geçiş/uyarı, `1` iş kuralı bloku, `2` şema veya sistem hatasıdır. `BLOCK` sonucunu atlama, bulguyu sessizce düşürme veya model muhakemesiyle hesap kodunu geçerli sayma. Aynı katalog ve aynı girdide sonuç, bulgu sırası ve `receipt_sha256` değişmemelidir. Parasal değerleri JSON dizgesi olarak ver; müşteri girdisini yalnızca yerel dosyadan oku.

## Ingest sistemi

Mizan, yevmiye veya diğer müşteri kayıtları geldiğinde önce [case-intake.md](references/case-intake.md) dosyasını oku. Müşteri kaydını vaka `documents/` dizinine koy ve `scope: case` manifestiyle yalnızca vaka korpusuna al. CSV/TSV/JSON/TXT, metin katmanlı PDF ve XLSX/XLSM yerelde çıkarılır; elektronik tablo formülleri korunur fakat çalıştırılmaz.

Manifesti doğrula ve içe al:

```powershell
python scripts/ingest_sources.py ingest --manifest sources.json --corpus .muhasebecim/corpus
python scripts/query_corpus.py --corpus .muhasebecim/corpus --query "amortisman"
```

2026 Mavi Kitap'tan olaya ilişkin standartların tam metin manifestini üret:

```powershell
python scripts/prepare_2026_tfrs_manifest.py --standards TMS-2 TMS-16 TFRS-15 --as-of YYYY-MM-DD --output tfrs-sources.json
```

Yalnızca kullanıcının sağladığı veya erişmeye yetkili olduğun belgeleri ingest et. Özgün dosyayı değiştirme. PDF metin çıkarımı başarısızsa OCR yapılmış gibi davranma; kaydı `extraction_pending` olarak bırak. Kişisel veri ve ticari sır içeren müşteri belgeleri için internet kaynağı ile aynı açık korpusu kullanma; vaka bazlı ayrı korpus oluştur.

## Muhakeme kuralları

- İşlem tarihi ile rapor tarihini karıştırma; her ikisini de açık yaz.
- KGK Mavi Kitap ile yürürlükteki metni, Kırmızı Kitap ile yayımlanmış fakat henüz yürürlüğe girmemiş hükümleri ayır.
- Taslakları ve kamuoyu görüş metinlerini yürürlükte kabul etme.
- Özelgeyi yalnızca idari görüş olarak etiketle; somut olay ve muhatap dışındaki bağlayıcılığını varsayma.
- VUK değerini TMS/TFRS ölçümü, Tekdüzen hesap kodunu finansal raporlama ölçüm ilkesi veya vergi kaydını yönetim raporu gibi sunma.
- Sektörel hesap planı bulunan banka, sigorta, finansal kuruluş ve benzeri işletmelerde genel Tekdüzen planını otomatik uygulama.
- Kaynak bulunamadığında madde numarası, oran veya kesin sonuç uydurma; doğrulanamayan kısmı açıkça sınırla.
- Kişisel ve ticari sır niteliğindeki verileri gereksiz yere kopyalama; örneklerde maskele.

## Teslim standardı

Önce kısa sonucu ver. Ardından uygulanan çerçeve ve dönem, doğrulanmış kaynaklar, muhakeme, Python hesap özeti, yevmiye kaydı, vergi mutabakatı, kontroller ve açık kalan hususları göster. Kullanıcı yalnızca kısa yanıt istese bile hesap izi dosyalarını üret ve sonuçta yollarını belirt.
