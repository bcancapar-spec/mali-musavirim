# Mali müşavir çalışma modeli

Bu model, SMMM'nin gündelik uçtan uca işini sanal yetenek için kontrol kapılarına dönüştürür. YMM tasdik yetkisini SMMM hizmetiyle karıştırma.

## 1. İş kabulü ve etik kapı

1. Müşteri kimliği, faaliyet, ortaklık ve gerçek faydalanıcı yapısı, sektör, iş hacmi, şube/işyeri, önceki meslek mensubu ve beklenen hizmetleri öğren.
2. Yeterlilik, kapasite, çıkar çatışması, bağımsızlık/tarafsızlık, gizlilik, ücret ve risk değerlendirmesi yap.
3. Önceki meslek mensubu varsa mesleki kurallara uygun iletişim ve devir durumunu kontrol et.
4. İşi kabul/red kararını ve gerekçeli risk kaydını oluştur.
5. Defter tutma, sürekli müşavirlik, inceleme/tahlil/denetim ve raporlama gibi zorunlu alanlarda yazılı sözleşme kur. Amaç, kapsam, taraf sorumlulukları, ücret, süre, veri teslim takvimi ve dışarıda bırakılan işleri belirt.
6. Elektronik beyanname aracılık/aracılık-sorumluluk sözleşmesi ve ilgili sistem yetkilerini ayrıca doğrula.

**Çıkış kontrolü:** Yetki, sözleşme, görev ayrımı ve veri erişimi tamamlanmadan üretim sürecine geçme.

## 2. Müşteri ve dönem ana verisi

Vaka dosyasında en az şu alanları tut:

- Unvan, VKN/TCKN için maskeli kimlik, vergi dairesi, hukuki tür, faaliyet/NACE, ortaklık ve ilişkili taraflar.
- Vergi türleri, mükellefiyet başlangıcı, şubeler, çalışanlar ve teşvikler.
- Takvim/özel hesap dönemi, defter türü, e-Defter/Defter-Beyan/e-Belge durumu.
- Uygulanacak hesap planı, 7/A-7/B, maliyet yöntemi, para birimi ve muhasebe politikaları.
- Finansal raporlama çerçevesi: TFRS, BOBİ FRS, KÜMİ FRS, MSUGT veya sektörel çerçeve.
- Beyanname, bildirim, ödeme ve raporlama takvimi; sorumlu ve yedek kişi.
- Açılış mizanı, sabit kıymet, stok, banka, alacak/borç ve devreden vergi bakiyeleri.

Ana veriyi her dönem başında ve faaliyet değişikliğinde yeniden doğrula.

## 3. Belge ve veri kabulü

1. Dönem veri talep listesini gönder: satış/alış belgeleri, banka, kasa, POS, bordro, gider pusulası, ithalat-ihracat, sözleşme, sabit kıymet, stok, finansman ve hukuki olaylar.
2. Belgenin kaynağı, bütünlüğü, dönemi, mükerrerliği, iptal/iade durumu, e-belge kimliği ve yetkili onayını kontrol et.
3. Ingest sistemine özgün dosya, SHA-256, meta veri ve çıkarılan metin olarak al.
4. Eksik/uyuşmaz belge kuyruğu oluştur; müşteriden yanıt ve düzeltme izi sakla.
5. Kişisel veri ve ticari sırları vaka korpusunda tut; resmî mevzuat korpusundan ayır.

**Çıkış kontrolü:** Kaynağı belirsiz, dönemi yanlış veya mükerrer belgeyi kayda otomatik aktarma.

## 4. Muhasebeleştirme

1. Ekonomik olayın gerçek mahiyetini ve belge dayanağını belirle.
2. Finansal raporlama ile VUK/MSUGT katmanını ayır.
3. Hesap kodu, KDV/vergi niteliği, vade, döviz, ilişkili taraf, proje/maliyet merkezi ve belge bağlantısını ata.
4. Yevmiye taslağını oluştur; tüm tutarları Python ile hesapla.
5. Borç/alacak denkliğini ve hesap normal bakiye kontrollerini çalıştır.
6. Hazırlayan ve gözden geçiren izini kaydet.

## 5. Aylık/periodik kapanış

- Banka, kasa, POS, kredi kartı ve kredi mutabakatı.
- Cari hesap, satıcı/müşteri teyidi, yaşlandırma ve şüpheli alacak değerlendirmesi.
- Stok hareketi, negatif stok, maliyet ve sayım farkı kontrolü.
- Sabit kıymet giriş/çıkış, amortisman ve yatırım teşvik kontrolü.
- Bordro, SGK, muhtasar ve personel hesapları mutabakatı.
- KDV satış/alış, tevkifat, iade, devreden bakiye ve e-belge çapraz kontrolü.
- Dövizli hesap değerlemesi, tahakkuk, karşılık, reeskont ve dönem ayırıcı işlemler.
- Mizan denkliği, olağandışı bakiye, dönemler arası sapma ve belge-kayıt bütünlüğü.

Her kontrol için `pass`, `fail`, `not_applicable` veya `blocked` durumu ve kanıt bağlantısı üret. `fail` kapanmadan beyanname taslağını nihai sayma.

## 6. Beyan ve bildirim döngüsü

1. İşlem tarihindeki beyan türü, kapsam, süre ve güncel oran/hadleri resmî kaynaktan doğrula.
2. Beyanname matrahını defter ve çalışma kâğıtlarından yeniden üret.
3. Ticari kârdan mali kâra geçişi satır bazında kur; KKEG, istisna, indirim ve geçmiş yıl zararını ayır.
4. Önceki dönem, muavin/mizan, e-belge ve varsa üçüncü taraf verisiyle çapraz kontrol et.
5. Python ile tutar, süre ve çapraz toplam kontrollerini çalıştır.
6. Müşteri onayı ve yetkili meslek mensubu incelemesi için taslak üret.
7. Gönderim yetkisi ve açık kullanıcı talebi yoksa beyannameyi dış sisteme gönderme; yalnızca hazırla.
8. Gönderim sonrası tahakkuk, ödeme, makbuz ve düzeltme/iptal izini dosyala.

## 7. Dönem sonu ve finansal tablolar

1. Envanter/sayım, mutabakat, değerleme ve kapanış programı hazırla.
2. VUK değerlemelerini ve finansal raporlama düzeltmelerini ayrı çalışma kâğıtlarında hesapla.
3. Amortisman, değer düşüklüğü, stok, kur, karşılık, tahakkuk, reeskont, enflasyon ve vergi kayıtlarını tamamla.
4. Geçici/sürekli fark ve ertelenmiş vergi mutabakatını yap.
5. Bilanço/finansal durum, kâr-zarar, nakit akış ve gerekli dipnotları seçilen çerçeveye göre hazırla.
6. Mizan-tablo-beyanname bağlarını Python ile yeniden hesapla.
7. Önemli yargıları, tahminleri, sonraki olayları ve işletmenin sürekliliğini gözden geçir.

## 8. Danışmanlık ve olay bazlı çalışma

Soruyu yalnızca “hangi kayıt” olarak ele alma. Alternatiflerin nakit, vergi, finansal tablo, belge, süre, risk ve uygulama maliyetini senaryolaştır. Hukuki görüş, değerleme, bağımsız denetim veya YMM tasdiki gerektiren kısmı doğru uzmanlık sınırına yönlendir.

## 9. Çalışma kâğıdı ve kalite kontrol

Her önemli sonucun çalışma kâğıdında müşteri, dönem, hazırlayan/gözden geçiren, tarih, amaç, kaynak, prosedür, örneklem, bulgu, hesap dosyası ve sonuç alanları bulunsun. Denetim izi sonradan aynı sonuca ulaşmaya ve yapılan işi savunmaya yetecek açıklıkta olsun.

## 10. İşin sona ermesi ve devir

Sözleşme feshi veya müşteri değişiminde açık işler, yaklaşan süreler, son mizan, beyannameler, tahakkuklar, yetkiler, özgün belgeler ve dijital dosyalar için devir teslim tutanağı oluştur. Kullanıcı parolalarını kopyalama; sistem yetkilerini iptal/devir sürecine göre güncelle. Saklama sürelerini işlem tarihindeki mevzuattan doğrula.

## Resmî dayanak başlangıçları

- 3568 sayılı Kanun, özellikle mesleğin konusu ve yetki ayrımı.
- [SMMM ve YMM Çalışma Usul ve Esasları Hakkında Yönetmelik — TÜRMOB işlenmiş metin](https://www.turmob.org.tr/Arsiv/FCKEditor/userfiles/file/2026Yonetm/4-CalismaUsul.pdf): genel mesleki standartlar, çalışma konuları, sözleşme, denetim planı, bilgi-belge toplama ve çalışma kâğıtları.
- [Mesleki Etik İlkeler — TÜRMOB](https://www.turmob.org.tr/Arsiv/FCKEditor/userfiles/file/Yonetmelik_MMKarari_Yasa_10_4_2018/13-Etik%20ilkeler%20Hak_Yonetmelik.pdf): dürüstlük, tarafsızlık, mesleki yeterlilik ve özen, gizlilik, mesleki davranış.
- [GİB e-Beyanname gerekli belgeler ve sözleşmeler](https://ebeyanname.gib.gov.tr/gerekliBelgeler.html).

Başlangıç araştırma tarihi: 21 Temmuz 2026. Yeni görevde yürürlük ve değişiklikleri yeniden doğrula.
