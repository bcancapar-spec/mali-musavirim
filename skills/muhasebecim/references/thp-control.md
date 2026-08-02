# Tekdüzen hesap planı ve kayıt kontrolü

## Kapsamı doğrula

Önce işletmenin genel MSUGT Tekdüzen Hesap Planına mı, yoksa banka, sigorta, finansal kuruluş veya başka bir düzenleyicinin özel planına mı tabi olduğunu belirle. Genel plan dışında önerilen hesap kodu için düzenleyici dayanağı belirt.

## Hesap sınıfları

| Sınıf | İçerik |
|---|---|
| 1 | Dönen varlıklar |
| 2 | Duran varlıklar |
| 3 | Kısa vadeli yabancı kaynaklar |
| 4 | Uzun vadeli yabancı kaynaklar |
| 5 | Özkaynaklar |
| 6 | Gelir tablosu hesapları |
| 7 | Maliyet hesapları; 7/A veya 7/B seçeneği |
| 8 | Serbest hesaplar |
| 9 | Nazım hesaplar |

Üç haneli hesap ve alt hesap kullanımını işlem tarihinde yürürlükteki 1 Sıra No.lu MSUGT ve sonraki değişikliklerden doğrula. Planın boş bıraktığı bir kodu “standart hesap” gibi sunma.

## Kayıt kontrol listesi

- Belge tarihi, kayıt tarihi, dönem ve para birimini göster.
- Her satırda hesap kodu, hesap adı, borç, alacak ve açıklama bulunsun.
- Aynı satırda hem borç hem alacak tutarı kullanma.
- Toplam borç ile toplam alacağı `journal-check` işlemiyle doğrula.
- Aktif/pasif düzenleyici hesap işaretini ve normal bakiye yönünü kontrol et.
- Kısa/uzun vade, ilişkili taraf, döviz, KDV ve maliyet merkezi alt hesaplarını gerektiğinde ayır.
- Finansal raporlama düzeltmesini yasal defter kaydı gibi göstermeden önce kayıt katmanını belirt.
- 7/A veya 7/B seçimini ve yansıtma hesaplarını tutarlı uygula.
- Dönem sonu kapanış, açılış ve ters kayıt gereksinimini açıkla.

## Sunum biçimi

| Hesap | Açıklama | Borç | Alacak | Katman |
|---|---|---:|---:|---|
| 000 | Örnek hesap — gerçek kodu doğrula | 0,00 | 0,00 | VUK/MSUGT veya raporlama düzeltmesi |

Tablodaki toplamları elle yazma; Python çıktısından aktar. Ardından kaydın ekonomik gerekçesini ve vergi etkisini ayrı paragraflarda açıkla.
