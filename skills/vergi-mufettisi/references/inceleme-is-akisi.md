# Vergi incelemesi hazırlık ve çalışma akışı

## 1. Kabul ve kapsam

Modu, mükellefi, görevlendirme/bildirim referansını, inceleme türünü, vergi türlerini, dönemleri, gerekçeyi ve teslimi yaz. Kapsam dışı alanları ayrı listele. Vergi, ceza, uzlaşma ve diğer değişken tutarları sabit kodlama.

## 2. Hak, gizlilik ve delil koruma

Kimlik/yetki, yazılı talep, kapsamı öğrenme, süre, tutanak, açıklama ve gizlilik kontrollerini çalışma programına al. Dosyalara salt-okunur özgün kopya, SHA-256, edinim kaynağı, edinim tarihi ve erişim kaydı ata.

## 3. Risk hipotezi matrisi

Her satırda risk, beklenen normal durum, test edilecek veri, prosedür, örneklem evreni, tolerans, lehe/aleyhe kanıt ve sonuç alanı olsun. Risk skorunu Python ile hesapla; skor tek başına vergi farkı veya hukuka aykırılık kanıtı değildir.

## 4. Veri zinciri ve mutabakat

Asgari zincir:

1. e-Defter/yevmiye ve kebir,
2. mizan ve hesap muavinleri,
3. finansal tablolar,
4. vergi beyannameleri,
5. tahakkuk ve ödemeler,
6. e-Fatura/e-Arşiv/e-İrsaliye ve benzeri belgeler,
7. banka, POS, stok, bordro, gümrük ve ilişkili taraf verileri,
8. resmî veya hukuka uygun üçüncü taraf verileri.

Her bağ için evren toplamı, eşleşen, eşleşmeyen, dönem farkı ve açıklanmamış farkı Python ile üret.

## 5. Örnekleme ve prosedür

Evreni ve seçim yöntemini açıkla. Rastgele seçimde tohumu, sistematik seçimde başlangıç/aralığı, parasal birim örneklemesinde tutar tabanını kaydet. Bilinmeyen evrende örneklem yeterliliği sonucu verme.

## 6. Bulgu ve mükellef açıklaması

Bulgu numarası, olgu, hukuki dayanak/pinpoint, veri ve belge referansları, Python hesap dosyası, vergi türü/dönem, lehe kanıt, mükellef açıklaması, karşı değerlendirme, olası etki ve açık kalemleri tut. Açıklamayı değiştirmeden sakla; yorumdan ayır.

## 7. Rapor ve kalite kapısı

Rapor taslağını kapsam, mevzuat, yöntem, bulgular, hesaplar, mükellef açıklamaları, sonuç ve ekler olarak düzenle. Her sayıyı hesap iziyle yeniden üret. Yetkili incelemede rapor değerlendirme komisyonu; hazırlık modunda ruhsatlı meslek/hukuk incelemesi tamamlanmadan dosyayı nihai sayma.
