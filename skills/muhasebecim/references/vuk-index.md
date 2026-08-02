# Vergi Usul Kanunu konu yönlendiricisi

Bu dosya kanun metni yerine geçmez. Madde numaralarını arama başlangıcı olarak kullan; işlem tarihindeki konsolide maddeyi, geçici maddeleri, genel tebliğleri ve yürürlük hükümlerini açarak doğrula.

## Konu haritası

| Konu | Başlangıç maddeleri |
|---|---|
| Vergi kanunlarının uygulanması, ispat | 3 |
| Vergi mahremiyeti | 5 |
| Mükellef, vergi sorumlusu, kanuni temsilci | 8-11 |
| Mücbir sebep ve süreler | 13-18 |
| Vergiyi doğuran olay | 19 |
| Tarh, tebliğ, tahakkuk | 20-28 |
| İkmalen, re'sen ve idarece tarh | 29-30 |
| Zamanaşımı | 113-114 |
| Vergi hataları, düzeltme ve şikâyet | 116-126 |
| Yoklama, vergi incelemesi ve bilgi toplama | 127-152 |
| İşe başlama/değişiklik/bırakma bildirimleri | 153-170 |
| Defter tutma, sınıflar ve defterler | 171-214 |
| Kayıt nizamı | 215-226 |
| Vesikalar, fatura ve diğer belgeler | 227-242 |
| Muhafaza ve ibraz | 253-257 |
| Elektronik kayıt/belge yetkisi | Mükerrer 257 |
| Elektronik tebligat | 107/A; 7587 sayılı Kanunun 9-11 inci maddeleri |
| Değerleme esasları | 258-330 |
| Maliyet bedeli | 262 |
| Emsal bedeli ve emsal ücreti | 267 |
| Gayrimenkuller ve tesisat | 269-272 |
| Emtia ve stok değer düşüklüğü | 274, 278 |
| Yabancı paralar | 280 |
| Alacaklar ve borçlar | 281, 285 |
| Karşılıklar | 288 |
| Finansal kiralama | Mükerrer 290 |
| Enflasyon düzeltmesi ve yeniden değerleme | Mükerrer 298, geçici maddeler |
| Amortisman | 313-321 |
| Şüpheli alacak | 323 |
| Vazgeçilen alacak | 324 |
| Yenileme fonu ve sigorta tazminatı | 328-329 |
| Vergi ziyaı ve cezası | 341, 344 |
| Usulsüzlük ve özel usulsüzlük | 351-355, mükerrer 355 |
| Kaçakçılık suçları | 359-367 |
| Yanılma, izaha davet, pişmanlık, ceza indirimi | 369-371, 376 |
| Özelge | 413 ve mükerrer 413 |
| Yıllık güncellenen maktu had ve cezalar | Mükerrer 414 |
| Uzlaşma | Ek maddeler |

## Bir konuyu tamamlama sırası

1. 213 sayılı Kanunun işlem tarihinde yürürlükte konsolide maddesini aç.
2. Maddede Bakanlığa/KGK'ye verilen düzenleme yetkisini tespit et.
3. İlgili genel tebliğ, sirküler, Resmî Gazete değişikliği ve geçici maddeyi ara.
4. Yıllık değişen tutar için ilgili yıl tebliğini doğrula. Örneğin 2026 uygulamasında 31 Aralık 2025 tarihli 588 Sıra No.lu VUK Genel Tebliğini başlangıç noktası olarak kontrol et; sonraki değişiklikleri de ara.
5. Özelge gerekiyorsa yalnızca benzer olay ve güncel mevzuatla birlikte idari görüş olarak kullan.
6. Hesaplama girdilerini kaynak meta verisiyle Python'a geçir.

## Sık ayrımlar

- **Amortisman:** TMS/BOBİ/KÜMİ yararlı ömür ve kalıntı değer yaklaşımı ile VUK oran/listesini ayrı hesapla.
- **Stok:** Finansal raporlama maliyet/NGD ölçümü ile VUK emtia değerlemesini ayrı incele.
- **Kur:** İşlem tarihi kuru, raporlama kuru ve VUK değerleme kurunun kaynağını ayır.
- **Şüpheli alacak:** TFRS 9 beklenen kredi zararı ile VUK 323 koşullarını birbirinin yerine kullanma.
- **Karşılık:** TMS 37 yükümlülük ölçümü ile VUK'ta indirilebilirlik şartlarını ayrı değerlendir.
- **Enflasyon:** TMS 29/BOBİ FRS raporlama düzeltmesi ile VUK mükerrer 298 ve geçici maddeler kapsamını ayrı motorlar gibi ele al.
- **Ticari-mali kâr:** Kanunen kabul edilmeyen gider, istisna/indirim ve geçici farkları satır bazında mutabıklaştır.

## Resmî başlangıç noktaları

- [Cumhurbaşkanlığı Mevzuat Bilgi Sistemi — 213 sayılı VUK](https://www.mevzuat.gov.tr/mevzuatmetin/1.4.213.pdf)
- [Gelir İdaresi Başkanlığı — Mevzuat](https://gib.gov.tr/mevzuat)
- [GİB — 509 Sıra No.lu e-Belge Tebliğinin güncel metni](https://cdn.gib.gov.tr/api/gibportal-file/file/getFile?objectKey=MEVZUAT_TEBLIGLER%2FUNIVERSAL%2F2026%2FMEVZUAT_TEBLIGLER_2026_VukTeb509_Guncel.pdf)

Son toplu doğrulama: 2 Ağustos 2026. 7587 sayılı Kanunla VUK 107/A, mükerrer 257 ve geçici 38'de 1 Temmuz 2026 itibarıyla yürürlüğe giren değişiklikler korpusa alınmıştır. Yeni görevde güncelliği yeniden doğrula.
