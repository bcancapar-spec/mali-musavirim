# TMS/TFRS konu yönlendiricisi

## Sürüm kuralı

2026 hesap döneminde yürürlükteki metinler için KGK **TFRS 2026 Seti (Mavi Kitap)** kullan. Kırmızı Kitap yayımlanmış fakat henüz yürürlüğe girmemiş değişiklikleri de içerir. KGK envanterine göre TFRS 18 ve TFRS 19, 1 Ocak 2027'de yürürlüğe girer; 2026 sonucuna erken uygulama hükmü ayrıca doğrulanmadan dahil etme.

## 2026 Mavi Kitap envanteri

TFRS: 1 İlk Uygulama; 2 Hisse Bazlı Ödemeler; 3 İşletme Birleşmeleri; 5 Satış Amaçlı Elde Tutulan Duran Varlıklar; 6 Maden Kaynakları; 7 Finansal Araçlar Açıklamalar; 8 Faaliyet Bölümleri; 9 Finansal Araçlar; 10 Konsolide Finansal Tablolar; 11 Müşterek Anlaşmalar; 12 Diğer İşletmelerdeki Paylar; 13 Gerçeğe Uygun Değer; 14 Düzenlemeye Dayalı Erteleme Hesapları; 15 Hasılat; 16 Kiralamalar; 17 Sigorta Sözleşmeleri.

TMS: 1 Finansal Tabloların Sunuluşu; 2 Stoklar; 7 Nakit Akış; 8 Muhasebe Politikaları, Tahminler ve Hatalar; 10 Raporlama Döneminden Sonraki Olaylar; 12 Gelir Vergileri; 16 Maddi Duran Varlıklar; 19 Çalışanlara Sağlanan Faydalar; 20 Devlet Teşvikleri; 21 Kur Değişiminin Etkileri; 23 Borçlanma Maliyetleri; 24 İlişkili Taraflar; 26 Emeklilik Fayda Planları; 27 Bireysel Finansal Tablolar; 28 İştirakler ve İş Ortaklıkları; 29 Yüksek Enflasyon; 32 Finansal Araçlar Sunum; 33 Hisse Başına Kazanç; 34 Ara Dönem; 36 Değer Düşüklüğü; 37 Karşılıklar ve Koşullu Kalemler; 38 Maddi Olmayan Duran Varlıklar; 39 Finansal Araçlar Muhasebeleştirme ve Ölçme; 40 Yatırım Amaçlı Gayrimenkuller; 41 Tarımsal Faaliyetler.

Yorumları KGK setindeki güncel TFRS Yorum/TMS Yorum dizininden konu bazında kontrol et.

## Konu haritası

| Konu | Öncelikle bakılacak metinler | Python işlemi |
|---|---|---|
| Stok maliyeti ve net gerçekleşebilir değer | TMS 2 | `weighted-average-inventory`, `fifo-inventory` |
| Maddi duran varlık, amortisman ve bileşenler | TMS 16; değer düşüklüğü için TMS 36 | `straight-line-depreciation`, `impairment` |
| Hasılat ve sözleşme yükümlülükleri | TFRS 15 | Olaya özgü nakit akışı ve dağıtım betiği |
| Kiralama | TFRS 16 | `present-value`, `effective-interest` |
| Finansal araç ve beklenen kredi zararı | TFRS 9; sunum TMS 32; açıklama TFRS 7 | Olaya özgü ECL betiği; `effective-interest` |
| Kur farkları | TMS 21 | `fx-valuation` |
| Borçlanma maliyeti | TMS 23 | Olaya özgü ağırlıklı oran betiği |
| Ertelenmiş vergi | TMS 12 | `deferred-tax`, `tax-reconciliation` |
| Yüksek enflasyon | TMS 29 | `index-restatement`; parasal pozisyon için olaya özgü betik |
| Karşılık ve iskonto | TMS 37 | `present-value` |
| Gerçeğe uygun değer | TFRS 13 | Veri ve değerleme tekniğine özgü betik |
| Konsolidasyon ve yatırımlar | TFRS 10-12, TMS 27-28 | Olaya özgü eliminasyon betiği |
| Sunum, politika ve sonraki olay | TMS 1, 7, 8, 10, 24, 34 | Açıklama ve sınıflama kontrolü |

## BOBİ FRS ve KÜMİ FRS

BOBİ FRS için [KGK BOBİ FRS 2021 Sürümü](https://www.kgk.gov.tr/DynamicContentDetail/5151/Bu%CC%88yu%CC%88k-ve-Orta-Boy-I%CC%87s%CC%A7letmeler-I%CC%87c%CC%A7in-Finansal-Raporlama-Standard%C4%B1-%28BOBI%CC%87-FRS%29) ile sonradan yayımlanan değişiklikleri birlikte kontrol et. Büyük işletme hadleri ve kripto varlık gibi konularda sonraki kurul kararlarını ayrıca doğrula.

KÜMİ FRS için [KGK KÜMİ FRS 2022 Sürümü](https://www.kgk.gov.tr/DynamicContentDetail/11692/Ku%CC%88c%CC%A7u%CC%88k-ve-Mikro-I%CC%87s%CC%A7letmeler-ic%CC%A7in-Finansal-Raporlama-Standard%C4%B1-%28KU%CC%88MI%CC%87-FRS%29) ve güncellemelerini kontrol et. TFRS sonucunu otomatik olarak BOBİ/KÜMİ sonucuna taşıma; ilgili bölümün basitleştirilmiş ölçümünü ayrı uygula.

## Kaynaklar

- [KGK TFRS 2026 Mavi Kitap](https://www.kgk.gov.tr/DynamicContentDetail/12044/TFRS-2026-Seti-Mavi-Kitap)
- [KGK TFRS 2026 Kırmızı Kitap](https://www.kgk.gov.tr/DynamicContentDetail/12043/TFRS-2025-Seti-K%C4%B1rm%C4%B1z%C4%B1-Kitap)
- [KGK standart envanteri, 31.12.2025](https://www.kgk.gov.tr/DynamicContentDetail/6726/Tu%CC%88rkiye-Muhasebe-Standartlar%C4%B1-Envanteri-%2831-12-2025-itibar%C4%B1yla%29)

Son toplu doğrulama: 2 Ağustos 2026. 1 Temmuz 2026 tarihli TFRS 18 uyumlu finansal tablo formatı ve 2026 taksonomi metinleri bu tarihte hâlâ `draft` olarak izlenir. Yeni görevde güncelliği yeniden doğrula.
