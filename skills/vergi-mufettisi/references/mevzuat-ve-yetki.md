# Vergi müfettişi mevzuat ve yetki haritası

Doğrulama tarihi: 2 Ağustos 2026. Her somut olayda işlem tarihindeki konsolide metni yeniden doğrula.

## Ana yetki dayanakları

- [213 sayılı Vergi Usul Kanunu](https://www.mevzuat.gov.tr/mevzuatmetin/1.4.213.pdf):
  - Madde 5: vergi mahremiyeti.
  - Madde 134: incelemenin amacı, ödenmesi gereken verginin doğruluğunu araştırmak, tespit etmek ve sağlamak.
  - Madde 135-138: yetkililer, kimlik, incelemeye tabi olanlar ve zaman.
  - Madde 139: incelemenin esas itibariyle dairede yapılması; işyerinde inceleme talebi ve yazılı ibraz usulü.
  - Madde 140: kapsam ve başlama bildirimi, inceleme usulü, raporun mevzuata aykırı olamaması, süreler ve rapor değerlendirme komisyonu.
  - Madde 141: inceleme tutanakları ve ilgilinin itiraz/mülahazaları.
  - Madde 142: aramalı incelemede gerekçeli istem ve sulh ceza hâkimi kararı.
  - Madde 256: defter, belge, elektronik kayıt, erişim ve okunabilirlik için gerekli bilgi/araçları ibraz.
  - Madde 359 ve 367: kaçakçılık fiilleri ile ceza kovuşturmasına ilişkin özel usul; yazılım yalnızca emareyi işaretler.
- [Vergi İncelemelerinde Uyulacak Usul ve Esaslar Hakkında Yönetmelik](https://ms.hmb.gov.tr/uploads/2022/03/Vergi-Incelemelerinde-Uyulacak-Usul-ve-Esaslar-Hakkinda-Yonetmelik.pdf): temel ilkeler, yazılı görevlendirme, hazırlık, inceleme dosyası, ibraz, tutanak, rapor ve süre.
- [VDK — Vergi Müfettişlerinin Görev ve Yetkileri](https://vdk.hmb.gov.tr/vergi-mufettislerinin-gorev-ve-yetkileri): vergi incelemesine ek olarak ayrı görevlendirmeye tabi teftiş, idari soruşturma, TPKK, suç gelirleri mevzuatı, araştırma ve eğitim görevleri.
- [VDK — Vergi İncelemesi Genel Bilgiler](https://vdk.hmb.gov.tr/vergi-incelemesi-genel-bilgiler): risk/veri temelli süreç, tam ve sınırlı inceleme ayrımı.
- [VDK — Mükellef Hakları](https://vdk.hmb.gov.tr/vergi-incelemesinde-mukellef-haklari) ve [Mükellef Yükümlülükleri](https://vdk.hmb.gov.tr/vergi-incelemesinde-mukellef-yukumlulukleri): güncel idari bilgilendirme.

## Norm çatışması uyarısı

HMB sitesindeki işlenmiş inceleme yönetmeliği PDF'i 7 Nisan 2021 değişikliklerini göstermektedir. Daha sonra değişen VUK 139'un konsolide metni incelemenin esas itibariyle dairede yapılacağını belirtirken PDF'deki eski 13 üncü madde işyerini esas alır. Bu nedenle yer, başlama ve süre gibi konularda güncel VUK'u üst ve daha yeni norm olarak kontrol et; eski PDF hükmünü otomatik kural yapma.

## Yazılımın yetki sınırı

Bu eklenti müfettiş unvanı veya kamu yetkisi kazandırmaz. `authorized_inspector_support` modu ancak kullanıcı gerçek görevlendirme kapsamı ve yetki kanıtını vaka dosyasına kaydettiğinde analitik destek verir. Aksi halde sonuç mükellef hazırlık çalışmasıdır.
