# Proje Amacı, Kapsamı ve Güncel Durumu

Bu belge Mali Müşavirim projesinin neden başlatıldığını, kullanıcı tarafından hangi kabiliyetlerin istendiğini, hedeflenen sistemi, bugüne kadar tamamlanan işleri, açık sınırları, henüz tamamlanmayan alanları ve gerçek muhasebe verisiyle yapılacak sonraki çalışmayı tek yerde açıklar.

## 1. Yönetici özeti

### Ne istedik?

Türk muhasebe ve vergi uygulamalarında çalışan; bir mali müşavirin dosya ele alma biçimini modelleyen; Tekdüzen Hesap Planı, VUK ve finansal raporlama standartlarını birbirine karıştırmadan değerlendiren; müşteri verisini yerelde tutan; bütün hesapları Python ile yapan; sonuçlarını kanıt, kural kimliği ve SHA-256 makbuzuyla açıklayan bir sanal muhakeme ve kontrol sistemi istedik.

Daha sonra bu hedefi şu uzmanlıklarla genişlettik:

- vergi müfettişi bakışıyla incelemeye hazırlık,
- YMM tasdik dosyası ve bağımsızlık kapıları,
- her vakada hukuka uygun mükellef lehine adım,
- mükellef aleyhine her hususta kullanıcı/SMMM/YMM için zorunlu yerel iç bildirim,
- Ortak Avukat projesindeki gibi model beyanına güvenmeyen deterministik kontrol kapıları,
- public GitHub yayını, mali müşavir rehberleri ve doğrulanabilir test yöntemi.

### Neyi hedefledik?

Tek bir soruya cevap veren bir sohbet metni değil, aşağıdaki zinciri uçtan uca yürüten bir çalışma sistemi hedefledik:

> Vaka kabulü → yerel belge ingest'i → kapsam ve çerçeve seçimi → resmî kaynak → Python hesabı → THP/VUK kontrolü → ticari-mali mutabakat → mükellef lehine adım → aleyhe iç bildirim → fiziksel kanıt ve hash → meslek mensubu incelemesine hazır dosya.

### Neyi başardık?

v0.0.3 itibarıyla yerel ingest, 14 işlemli Python hesaplama motoru, sürümlü THP/VUK motoru, vergi müfettişi ve YMM rol motoru, mükellef menfaati/iç bildirim motoru, vaka kapanış kapıları, üç Codex becerisi, ayrıntılı meslek rehberleri ve 72 testten oluşan public bir sistem tamamlandı.

### Şu anda ne yapıyoruz?

Kod ve dokümantasyon aşaması tamamlandı. Sıradaki iş, kullanıcının sağlayacağı gerçek fakat yerelde tutulacak muhasebe kayıtlarıyla ilk pilot vakayı çalıştırmaktır. Bu aşamada kolon eşlemesi, gerçek veri varyasyonları, yanlış pozitifler, eksik kurallar ve meslek mensubu geri bildirimi ölçülecektir.

## 2. Başlangıçta istenenler

Proje tek bir teknik taleple başlamadı. Birbiri üzerine eklenen aşağıdaki iş ihtiyaçlarından oluştu.

### 2.1 Sanal mali müşavir muhakemesi

İlk hedef, yalnız hesap yapan bir araç değil; mali müşavirin şu reflekslerini izleyen bir yetenek setiydi:

- işe başlamadan işletme, dönem, amaç ve önemliliği belirlemek,
- finansal raporlama ile vergi sonucunu ayırmak,
- belge, kayıt, mizan, mali tablo ve beyannameyi mutabıklaştırmak,
- eksik olgu ile yanlış sonucu birbirinden ayırmak,
- önerilen kaydı ve düzeltmeyi açıklamak,
- sonucu meslek mensubu incelemesine hazırlamak.

### 2.2 Bütün hesapların Python ile yapılması

Toplama, oran, KDV, amortisman, faiz, stok, kur, tarih, sıralama, örneklem ve mutabakat dâhil hiçbir sayısal işlemin modelin zihinsel hesabına bırakılmaması istendi.

Bu nedenle sistemde:

- parasal değerler `Decimal` ile işlenir,
- `float` para girdisi reddedilir,
- girdiler JSON dizgesi olarak alınır,
- yuvarlama yöntemi açıklanır,
- ara adımlar ve sonuçlar dosyalanır,
- girdi ve sonuç SHA-256 özetleri korunur.

### 2.3 Türk muhasebe ve vergi çerçevesi

Sistemden aşağıdaki katmanları öğrenmesi ve doğru yere yönlendirmesi istendi:

- Tekdüzen Hesap Planı ve MSUGT,
- Vergi Usul Kanunu,
- TMS/TFRS,
- BOBİ FRS,
- KÜMİ FRS,
- dönem sonu işlemleri,
- değerleme, amortisman, stok ve kur işlemleri,
- vergi karşılığı ve ticari kârdan mali kâra geçiş.

Temel tasarım kararı, bu katmanları tek bir “muhasebe doğrusu” içinde eritmemektir. THP hesap kodu, finansal raporlama ölçümü ve VUK vergi sonucu ayrı değerlendirilir.

### 2.4 Yerel ingest sistemi

İncelenecek verilerin cihazdan çıkmaması istendi. Sistem şu ilkeye göre kuruldu:

- müşteri belgesi yalnız yerel dosya sisteminde tutulur,
- uzak OCR, LLM, embedding veya analiz hizmetine gönderilmez,
- ağ yalnız açık resmî kaynakların indirilmesinde kullanılır,
- özgün belge değiştirilmez,
- belge hash'i, metin çıkarımı ve sürüm izi saklanır,
- gerçek müşteri verisi GitHub dışında tutulur.

### 2.5 Uçtan uca ve anahtar teslim çalışma

İşin tek bir raporla bitmemesi; vaka klasörünün oluşturulması, girdilerin alınması, hesapların çalıştırılması, bulguların düzeltilmesi ve bütün kapılar geçince dosyanın profesyonel incelemeye hazır hâle gelmesi istendi.

### 2.6 Deterministik THP kural motoru

THP'nin yalnız açıklama metni olarak değil, Python ile çalışan bir kural motoruna dönüştürülmesi istendi. Ortak Avukat projesindeki şu yöntemlerden ilham alındı:

- açık kural kimlikleri,
- kapalı veri şemaları,
- fiziksel kanıt,
- fail-closed karar,
- aynı girdide aynı sonuç,
- modelin “yaptım” beyanı yerine script kontrolü.

Muhasebe motoru bağımsız olarak sıfırdan yazıldı; diğer projenin kodu kopyalanmadı.

### 2.7 Vergi müfettişi ve YMM uzmanlıkları

Vergi incelemesine hazırlık ile YMM tasdik sürecinin genel muhasebe yardımından ayrı yetenekler olması istendi. Bu nedenle üç rol oluşturuldu:

- `$muhasebecim`,
- `$vergi-mufettisi`,
- `$yeminli-mali-musavir`.

### 2.8 Mükellef menfaati ve iç bildirim

Sistemin her zaman hukuka uygun mükellef lehine adımı hazırlaması; aleyhe her hususta mali müşaviri veya kullanıcıyı “iç istihbarat” çalışma kaydında bilgilendirmesi istendi.

Bu istek şu güvenli biçimde uygulandı:

- lehe hak, delil, düzeltme, açıklama veya başvuru adımı hazırlanır,
- aleyhe olgu iç analizden saklanmaz,
- kullanıcı/SMMM/YMM alıcısı belirlenir,
- görülme kaydı alınır,
- risk bir koruma adımına bağlanır,
- iç kayıt otomatik dışarı gönderilmez,
- kanunen zorunlu kayıt, beyan veya raporlama gizlenmez,
- vergi müfettişi tarafsızlığı ve YMM bağımsızlığı korunur.

### 2.9 Public GitHub ve meslek dilinde açıklama

Sistemin public GitHub deposunda yayımlanması; ne işe yaradığının, nasıl kullanıldığının ve muhasebecilerin konuya nasıl vakıf olacağının ayrıntılı biçimde anlatılması istendi.

Bu nedenle teknik README'nin yanında yazılımı çalıştırmadan örnek vaka üzerinden öğrenme, mali müşavir kullanımı, YMM/vergi müfettişi, mükellef menfaati ve test metodolojisi belgeleri oluşturuldu.

## 3. Hedeflenen ürün tanımı

Mali Müşavirim'in hedefi bir muhasebe ERP'si olmak değildir. Hedef, mevcut muhasebe verisinin üzerine çalışan yerel bir kontrol, muhakeme ve çalışma kâğıdı katmanı olmaktır.

### 3.1 Hedef kullanıcılar

- Serbest Muhasebeci Mali Müşavirler,
- Yeminli Mali Müşavirler ve tasdik ekipleri,
- muhasebe bürosu personeli,
- işletme içi muhasebe ve finans ekipleri,
- vergi incelemesine hazırlanan mükellefler,
- gerçek yetki kanıtı bulunan vergi inceleme personelinin analitik çalışma dosyaları,
- teknik denetim izi ve veri dönüşümü hazırlayan ekipler.

### 3.2 Hedef çıktı

İdeal çıktı tek bir cevap değildir. Bir vaka sonunda aşağıdaki dosya seti hedeflenir:

- kapsam ve olgular,
- resmî kaynak ve yürürlük kaydı,
- özgün belge hash'leri,
- Python hesap girdisi, kodu ve sonucu,
- önerilen yevmiye/düzeltme kaydı,
- THP/VUK bulguları,
- ticari-mali mutabakat,
- vergi incelemesi veya YMM çalışma kâğıdı,
- mükellef lehine adım,
- varsa aleyhe yerel iç bildirim,
- sonuç makbuzları,
- kapanış kontrolü.

### 3.3 Başarı tanımı

Bir dosya aşağıdaki koşullarda başarılı sayılır:

- sonucu etkileyen eksik olgular görünürdür,
- kullanılan mevzuat ve dönem açıktır,
- her sayı Python ile yeniden üretilebilir,
- hesap ve kayıt kapıları çalışmıştır,
- finansal raporlama ile vergi sonucu ayrılmıştır,
- hukuka uygun mükellef koruma adımı hazırlanmıştır,
- aleyhe husus gizlenmeden yetkili insana bildirilmiştir,
- fiziksel çalışma kâğıtları ve hash'leri doğrulanmıştır,
- dosya yalnız “meslek mensubu incelemesine hazır” statüsüne gelmiştir.

## 4. Değişmeyen tasarım ilkeleri

### 4.1 Yerel veri

Müşteri verisi buluta gönderilmez. `cases/`, `corpus/` ve yaygın muhasebe veri dosyaları GitHub dışında tutulur.

### 4.2 Python hesap izi

Bütün sayısal işlemler çalıştırılan Python koduna dayanır. Elektronik tablo formülü veya dil modeli sayısal doğruluk kaynağı değildir.

### 4.3 Resmî kaynak ve tarih

Oran, had, kur, süre ve yürürlük ezberden alınmaz. İşlem tarihinde doğrulanan kaynak açık girdi hâline getirilir.

### 4.4 Katman ayrımı

THP, VUK ve finansal raporlama standartları birbirinin yerine kullanılmaz.

### 4.5 Fail-closed

Kanıtlanmayan durum otomatik olarak uygun sayılmaz. Eksik şema `ERROR`, geçerli girdide zorunlu kontrol eksikliği `BLOCK` üretir.

### 4.6 Determinizm

Aynı girdi ve katalog aynı normalize edilmiş sonuç, bulgu sırası ve SHA-256 makbuzunu üretmelidir.

### 4.7 İç dürüstlük ve dış koruma

Aleyhe husus iç analizde saklanmaz. Dış taslak ise mükellefi gereksiz yere zayıflatan, zorunlu olmayan ikrar veya ifadelerle kurulmaz. Bu ayrım gerçeğe aykırı kayıt ya da zorunlu açıklamayı gizleme yetkisi vermez.

### 4.8 İnsan yetkisi

Yazılım beyan, imza, mühür, tasdik, resmî inceleme veya kamu yetkisi kullanmaz.

## 5. Bugüne kadar başardıklarımız

Bu bölümdeki sayılar 2 Ağustos 2026 tarihinde Python ile katalog ve test dosyalarından yeniden sayılmıştır.

| Ölçü | Tamamlanan |
|---|---:|
| Public sürüm | `v0.0.3` |
| Codex uzmanlık becerisi | 3 |
| Python hesaplama işlemi | 14 |
| Tanımlı genel THP hesabı | 271 |
| THP proje hesabı aralığı | 2 |
| THP kaynak kaydı | 10 |
| Vergi müfettişi kuralı | 20 |
| YMM kuralı | 28 |
| Toplam profesyonel rol kuralı | 48 |
| Profesyonel rol kaynağı | 17 |
| Mükellef menfaati/iç bildirim kuralı | 16 |
| Mükellef menfaati kaynak kaydı | 5 |
| Otomatik test | 72 |
| Başarılı test | 72 |

### 5.1 Yerel ingest sistemi

Tamamlanan yetenekler:

- açık resmî internet kaynağı ingest'i,
- yalnız yerel vaka dosyası ingest'i,
- kaynak ve vaka kapsamı ayrımı,
- SHA-256 ile özgün belge izi,
- sürüm ve tekrar kontrolü,
- CSV, TSV, JSON ve TXT çıkarımı,
- metin katmanlı PDF çıkarımı,
- XLSX/XLSM hücre/formül çıkarımı,
- elektronik tablo formüllerini çalıştırmama,
- yerel korpus araması,
- ağ adresini vaka verisi olarak reddetme.

### 5.2 Python hesaplama çekirdeği

Tamamlanan 14 işlem:

1. gün hesabı,
2. normal amortisman,
3. azalan bakiyeler amortismanı,
4. bugünkü değer,
5. etkin faiz,
6. hareketli ağırlıklı ortalama stok,
7. FIFO stok,
8. kur değerlemesi,
9. endeksleme/enflasyon düzeltme hesabı,
10. değer düşüklüğü,
11. ertelenmiş vergi,
12. ticari-mali kâr mutabakatı,
13. KDV ayrıştırması,
14. yevmiye denkliği.

### 5.3 THP/VUK kural motoru

Tamamlanan motor işlemleri:

- katalog denetimi,
- hesap doğrulama,
- yevmiye doğrulama,
- mizan doğrulama.

Kontrol edilen başlıca alanlar:

- hesap kodu ve adı,
- genel THP kapsamı,
- sektör politikası,
- 7/A ve 7/B ayrımı,
- hesabın yürürlük tarihi,
- normal bakiye,
- borç/alacak denkliği,
- açılış-hareket-kapanış devri,
- kayıt dili ve defter para birimi,
- yanlış kaydın muhasebe usulüyle düzeltilmesi,
- yevmiye satır sıra/tekrar kontrolü,
- sağlanan kayıt tarih politikası,
- belge ve tevsik alanları.

### 5.4 Vaka çalışma döngüsü

`case_workflow.py` ile:

- standart vaka klasörü açılır,
- kapsam/olgu kapısı çalışır,
- kaynak kaydı aranır,
- muhakeme çalışma kâğıdı aranır,
- Python hesap zarfı doğrulanır,
- gerekli THP/VUK sonucu doğrulanır,
- gerekli vergi müfettişi ve YMM sonucu doğrulanır,
- mükellef menfaati sonucu her vakada zorunlu tutulur,
- açık kalemler kontrol edilir,
- yalnız bütün kapılar geçerse `ready_for_professional_review` statüsü verilir.

### 5.5 Vergi müfettişi yeteneği

İki çalışma modu tamamlandı:

- `taxpayer_readiness`: mükellef/SMMM için incelemeye hazırlık,
- `authorized_inspector_support`: gerçek görevlendirme kanıtı bulunan yetkili kullanıcıya analitik destek.

20 kural; yetki, görevlendirme, başlama bildirimi, kapsam, güncel mevzuat, gizlilik, yerel veri, risk hipotezi, mutabakat, ibraz, kanıt, mükellef hakları, süre, örneklem, bulgu, açıklama, VUK 359 eskalasyonu ve rapor inceleme kapılarını kapsar.

### 5.6 YMM yeteneği

İki çalışma modu tamamlandı:

- `pre_certification_readiness`: mükellef/SMMM için tasdik öncesi hazırlık,
- `licensed_ymm_support`: gerçek YMM çalışma dosyasına analitik destek.

28 kural; ruhsat, çalışanlar listesi, mühür, sözleşme, bağımsızlık, ilişki engeli, defter tutma ayrımı, kapsam, güncel tebliğ, önemlilik, plan, kayıt, mali tablo/beyanname mutabakatı, kanıt, örneklem, karşıt inceleme ve rapor kalite kapılarını kapsar.

### 5.7 Mükellef menfaati ve iç bildirim motoru

16 kural ile:

- en az bir lehe adım zorunlu tutulur,
- hazırlanmamış veya süresi geçmiş adım geçerli sayılmaz,
- aleyhe husus için yerel iç bildirim aranır,
- kullanıcı/SMMM/YMM alıcısı aranır,
- görülme kaydı ve tarihi doğrulanır,
- aleyhe husus aktif koruma adımına bağlanır,
- otomatik dış iletim engellenir,
- yerel işleme zorunlu tutulur,
- aleyhe olgu gizleme engellenir,
- hukuka uygunluk, tarafsızlık, bağımsızlık ve insan incelemesi korunur.

Modelin “hazırladım” demesi yeterli değildir. Lehe adım ve iç bildirim:

- vaka içinde fiziksel UTF-8 JSON dosyası olmalı,
- `action_id` veya `matter_id` motor sonucuyla eşleşmeli,
- SHA-256 özeti eşleşmeli,
- dosya vaka dizini dışına çıkmamalıdır.

### 5.8 Test ve dokümantasyon

72 testin tamamı geçmektedir. Test yöntemi:

- pozitif geçiş,
- negatif/fail-closed,
- kapalı şema,
- deterministik tekrar,
- katalog kurcalama,
- sonuç makbuzu,
- fiziksel dosya/hash,
- CLI çıkış kodları,
- vaka entegrasyonu,
- yerel ingest

kontrollerini kapsar.

Mali müşavirler için ayrıca:

- ayrıntılı kullanım rehberi,
- yazılımı çalıştırmadan örnek vaka rehberi,
- vergi müfettişi/YMM rehberi,
- mükellef menfaati rehberi,
- test yöntem ve sonuç belgesi,
- makinece okunabilir test kaydı

yayımlandı.

## 6. Sürüm yolculuğu

### v0.0.1 — İlk public pilot

- temel muhasebecim becerisi,
- yerel ingest,
- Python hesap motoru,
- vaka akışı,
- THP/VUK motoru,
- ilk mali müşavir rehberi.

### v0.0.2 — Profesyonel rol sistemi

- vergi müfettişi becerisi,
- YMM becerisi,
- 48 profesyonel rol kuralı,
- yetki, ruhsat, bağımsızlık ve rapor kapıları,
- Codex eklenti manifesti.

### v0.0.3 — Mükellef menfaati ve iç bildirim

- her vakada zorunlu hukuka uygun lehe adım,
- aleyhe hususta zorunlu yerel iç bildirim,
- fiziksel dosya ve SHA-256 bağı,
- kapatılamayan vaka kapısı,
- 16 deterministik kural,
- 72 test ve ayrıntılı test yöntemi,
- mali müşavir için genişletilmiş eğitim belgeleri.

## 7. Ne başaramadık veya henüz tamamlamadık?

Bu bölüm projenin zayıflıklarını saklamamak için açıkça yayımlanır.

### 7.1 Gerçek müşteri verisi pilotu henüz yapılmadı

Motorlar kurgusal, maskeli ve kontrollü test verileriyle doğrulandı. Kullanıcının sağlayacağı gerçek mizan, yevmiye veya belge seti henüz işlenmedi.

Bu nedenle henüz ölçülmeyen konular:

- farklı muhasebe programlarının kolon adları,
- gerçek dosyalardaki eksik veya bozuk satırlar,
- büyük veri hacmindeki çalışma süresi,
- gerçek kullanıcı açısından yanlış pozitif/negatif bulgular,
- özel hesap kırılımları,
- işletmeye özgü belge ve açıklama kalitesi.

### 7.2 Bütün Türk vergi mevzuatı deterministik kurala çevrilmedi

VUK ve meslek mevzuatının seçilmiş, açık ve makinece kontrol edilebilir alanları kodlandı. Gelir, kurumlar, KDV, damga, ÖTV, SGK, teşvik ve uluslararası vergi mevzuatının tamamı kural motorunda değildir.

### 7.3 TMS/TFRS'nin tamamı kural motoru değildir

TMS/TFRS, BOBİ FRS ve KÜMİ FRS için kaynak yönlendirmesi ve hesaplama çekirdeği vardır. Standartların bütün paragraf ve dipnot kontrolleri deterministik kurallara çevrilmemiştir.

### 7.4 Sektörel hesap planları yoktur

Mevcut katalog genel MSUGT THP içindir. Banka, sigorta, katılım finans, finansal kiralama, faktoring ve sermaye piyasası gibi özel hesap planları ayrıca kodlanmamıştır. Sistem bu alanlarda genel THP'yi uygulamak yerine blok verir.

### 7.5 Beyanname ve kurum sistemlerine canlı entegrasyon yoktur

Sistem:

- GİB'e bağlanmaz,
- e-Beyanname göndermez,
- e-Defter berat göndermez,
- e-Fatura düzenlemez,
- KDV iade/tasdik raporu sunmaz,
- VDK veya YMM portalında işlem yapmaz.

### 7.6 Belge gerçekliği veya sahtecilik sonucu vermez

Hash, dosyanın değişip değişmediğini gösterir; belgenin gerçek olduğunu göstermez. Sistem sahte belge veya vergi suçu hakkında nihai hukuki sonuç vermez.

### 7.7 Bağımsız güvenlik ve performans denetimi yapılmadı

Yerel veri, path traversal ve hash kontrolleri test edilmektedir. Ancak haricî sızma testi, bağımsız kod denetimi ve yüksek hacimli performans testi henüz yoktur.

### 7.8 Meslek yetkisi üretilemez

Sistem hiçbir sürümde:

- SMMM/YMM ruhsatı,
- imza veya mühür,
- beyanname sorumluluğu,
- tasdik görüşü,
- kamu vergi inceleme yetkisi

üstlenemez. Bu eksiklik değil, hukuki ve mesleki sınırdır.

## 8. Şu anda ne yapıyoruz?

Şu anki çalışma durumu:

1. v0.0.3 kodu ve belgeleri public GitHub deposunda yayımlandı.
2. Test sayısı ve yöntemleri repoda görünür hâle getirildi.
3. Yerel çalışma, THP/VUK, profesyonel roller ve mükellef menfaati kapıları tamamlandı.
4. Gerçek muhasebe verisi pilotu için sistem hazır.
5. Kullanıcının paylaşacağı kayıt ve dosya biçimi bekleniyor.

Aktif hedef yeni bir mevzuat iddiası eklemek değil; önce gerçek veri üzerinde mevcut sistemin davranışını ölçmek ve doğrulamaktır.

## 9. Sonraki aşama: gerçek muhasebe kayıtları pilotu

### 9.1 Kullanıcıdan beklenecek bilgiler

- veri türü: mizan, yevmiye, hesap listesi, fatura veya başka kayıt,
- dosya biçimi: XLSX, CSV, JSON, PDF veya metin,
- hesap dönemi ve işlem tarihleri,
- işletme türü ve sektör,
- genel THP veya özel hesap planı,
- finansal raporlama çerçevesi,
- inceleme amacı,
- önemlilik,
- kolonların anlamı,
- varsa beklenen hata veya kontrol sorusu.

Gereksiz kişisel veriler maskelenmeli; gerçek müşteri dosyaları GitHub'a eklenmemelidir.

### 9.2 Pilotun çalışma sırası

1. Yerel vaka klasörü oluşturulur.
2. Özgün dosya hash'i alınır.
3. Kolonlar kullanıcıyla doğrulanır.
4. Yerel ingest çalıştırılır.
5. Girdi normalizasyonu Python ile yapılır.
6. Toplamlar ve mutabakatlar Python ile yeniden hesaplanır.
7. THP/VUK motoru çalıştırılır.
8. Finansal raporlama ve vergi katmanı ayrılır.
9. Bulgular SMMM bakışıyla incelenir.
10. Hukuka uygun lehe adım hazırlanır.
11. Aleyhe hususlar yerel iç bildirimde gösterilir.
12. Fiziksel dosya/hash kapıları çalıştırılır.
13. Kullanıcı geri bildirimi alınır.
14. Yanlış pozitifler ve eksik kurallar için ayrı geliştirme kaydı oluşturulur.

### 9.3 Pilot başarı ölçütleri

- veri kaybı olmadan ingest,
- kolonların doğru eşlenmesi,
- toplamların kaynak programla mutabakatı,
- tekrar üretilebilir Python hesabı,
- açıklanabilir THP/VUK bulgusu,
- kritik yanlış pozitif bulunmaması,
- meslek mensubunun lehe adım ve iç bildirimi anlayabilmesi,
- gerçek müşteri verisinin cihaz dışına çıkmaması,
- vaka kapanış makbuzlarının doğrulanması.

## 10. Sonraki geliştirme yol haritası

Yol haritası gerçek veri pilotundan çıkacak bulgulara göre önceliklendirilecektir.

### Aşama A — Gerçek veri uyarlayıcıları

- yaygın muhasebe programı kolon eşlemeleri,
- hesap kodu normalizasyonu,
- tarih ve belge türü dönüşümü,
- borç/alacak veya bakiye gösterim farkları,
- büyük dosya ve bozuk satır raporlaması.

### Aşama B — Kural kapsamını genişletme

- beyanname-mizan mutabakatları,
- KDV kontrol paketleri,
- e-Belge ve e-Defter yapısal kontrolleri,
- dönem sonu kontrol paketleri,
- işlem türü bazlı tevsik ve belge matrisleri.

Her yeni kural, işlem tarihindeki resmî kaynağa bağlanmadan yayımlanmayacaktır.

### Aşama C — Finansal raporlama kontrol paketleri

- seçilmiş TMS/TFRS konu paketleri,
- BOBİ FRS/KÜMİ FRS fark matrisi,
- dipnot ve sunum kontrol listeleri,
- finansal raporlama ile VUK farklarının otomatik çalışma kâğıtları.

### Aşama D — Kalite ve güvenlik

- farklı desteklenen Python sürümlerinde CI,
- statik analiz ve kod kalite kontrolleri,
- bağımlılık güvenlik taraması,
- daha geniş path/girdi saldırı testleri,
- performans ve büyük dosya testleri,
- bağımsız meslek mensubu kabul testi.

## 11. Proje ne değildir?

Yanlış beklentiyi önlemek için:

- muhasebe ERP'si değildir,
- otomatik beyanname gönderim sistemi değildir,
- hukuk veya vergi görüşü garantisi değildir,
- belge gerçekliği tespit laboratuvarı değildir,
- resmî vergi inceleme aracı değildir,
- YMM tasdik makamı değildir,
- meslek mensubunun kararını otomatik olarak geçersiz kılan bir sistem değildir.

Proje; veri, kural, hesap ve kanıt zincirini düzenleyen, mekanik hatayı görünür kılan ve karar materyalini meslek mensubuna hazırlayan yerel ikinci göz sistemidir.

## 12. Bugünkü sonuç

İlk talepte tarif edilen sanal mali müşavir çekirdeği, yerel ingest, Python hesaplama, genel THP/VUK motoru, vergi müfettişi/YMM uzmanlıkları, mükellef menfaati/iç bildirim kapısı, test sistemi ve GitHub dokümantasyonu tamamlandı.

Tamamlanmış ürün hâlâ kontrollü pilot aşamasındadır. Bir sonraki gerçek değer noktası, kullanıcının sağlayacağı gerçek muhasebe kayıtlarıyla yapılacak ilk yerel vaka ve bu vakadan üretilecek mesleki geri bildirimdir.

Projenin bugün verdiği en doğru söz şudur:

> Tanımlı girdiyi yerelde işler, hesabı Python ile yeniden üretir, kodlanmış kuralları deterministik biçimde çalıştırır, mükellefin hukuka uygun koruma adımını hazırlar, aleyhe hususu yetkili insandan saklamaz ve profesyonel sorumluluğu yazılıma devretmez.
