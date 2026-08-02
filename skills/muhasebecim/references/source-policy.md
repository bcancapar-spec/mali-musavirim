# Resmî kaynak ve sürüm politikası

## Kaynak önceliği

Mevzuat ve standart sonucunu aşağıdaki öncelikle doğrula:

1. Resmî Gazete ve Cumhurbaşkanlığı Mevzuat Bilgi Sistemi.
2. KGK'nin yürürlükte standart setleri ve kurul kararları.
3. Gelir İdaresi Başkanlığının güncel kanun, tebliğ, sirküler ve rehber metinleri.
4. Konuya göre TCMB, TÜİK, Ticaret Bakanlığı, SGK ve diğer yetkili kurumların resmî verileri.
5. Danıştay, Anayasa Mahkemesi veya diğer resmî karar veri tabanları.

İkincil kaynakları arama ve çapraz kontrol için kullan; kesin hükmü mümkün olduğunda birincil metinden kur. Arama sonucu özetini, taslak metni veya eski sürümü nihai kaynak sayma.

## Zaman ve yürürlük kontrolü

Her görevde önce `as_of_date` belirle. Aşağıdaki alanları kaynak kaydında tut:

```json
{
  "authority": "KGK",
  "title": "TFRS 2026 Seti (Mavi Kitap)",
  "url": "https://www.kgk.gov.tr/DynamicContentDetail/12044/TFRS-2026-Seti-Mavi-Kitap",
  "publication_date": null,
  "effective_from": "2026-01-01",
  "effective_to": null,
  "accessed_at": "YYYY-MM-DD",
  "status": "in_force",
  "pinpoint": "TMS 16, paragraf ...",
  "notes": ""
}
```

`status` değerini `in_force`, `future`, `draft`, `repealed` veya `administrative_view` olarak seç. Aynı düzenlemenin değişiklik metniyle konsolide metnini karşılaştır; yürürlük maddesini ayrıca kontrol et.

## Değişken veri kuralı

Şu girdileri beceriye gömülü sabit değerlerden alma: vergi oranları, istisna ve beyan hadleri, cezalar, gecikme oranları, amortisman oran/listeleri, yeniden değerleme oranı, Yİ-ÜFE endeksleri, döviz kurları, asgari ücret ve SGK parametreleri.

İşlem tarihi için yetkili kaynaktan doğrula. Python girdi dosyasında değerin yanında `source_url`, `effective_from`, `effective_to` ve `accessed_at` alanlarını sakla. Geçmiş dönem hesabında bugünkü oranı kullanma.

## Özelge ve yargı kararı

Özelgeyi kanun yerine koyma. Tarihini, sayısını, somut olay benzerliğini ve sonraki mevzuat değişikliğini kontrol et; `administrative_view` olarak etiketle. Yargı kararında daire/kurul, esas-karar numarası, tarih, kesinleşme veya içtihat niteliği ve olay benzerliğini belirt.

## 2 Ağustos 2026 doğrulama kayıtları

- Yürürlükteki yıllık TFRS metni: [KGK TFRS 2026 Seti (Mavi Kitap)](https://www.kgk.gov.tr/DynamicContentDetail/12044/TFRS-2026-Seti-Mavi-Kitap).
- Yayımlanmış gelecek hükümleri de gösteren set: [KGK TFRS 2026 Seti (Kırmızı Kitap)](https://www.kgk.gov.tr/DynamicContentDetail/12043/TFRS-2025-Seti-K%C4%B1rm%C4%B1z%C4%B1-Kitap).
- Standart envanteri: [KGK, 31.12.2025 itibarıyla envanter](https://www.kgk.gov.tr/DynamicContentDetail/6726/Tu%CC%88rkiye-Muhasebe-Standartlar%C4%B1-Envanteri-%2831-12-2025-itibar%C4%B1yla%29).
- VUK konsolide metin başlangıç adresi: [Mevzuat Bilgi Sistemi, 213 sayılı Kanun](https://www.mevzuat.gov.tr/mevzuatmetin/1.4.213.pdf).
- VUK ikincil düzenlemeleri: [GİB Mevzuat](https://gib.gov.tr/mevzuat).
- VUK 107/A ve mükerrer 257 değişikliği: [7587 sayılı Kanun](https://cdn.gib.gov.tr/api/gibportal-file/file/getFile?objectKey=MEVZUAT_MADDE%2FUNIVERSAL%2F2026%2F7587.pdf).
- TFRS 18 uyumlu finansal tablo formatı ve taksonomi çalışması: KGK 1 Temmuz 2026 duyurusu; 2 Ağustos 2026 itibarıyla `draft`.
- 4 Temmuz 2026 vergi güncellemeleri: 333, 334 ve 335 Seri No.lu GVK Genel Tebliğleri, 26 Seri No.lu KVK Genel Tebliği ve Bazı Varlıkların Ekonomiye Kazandırılması Hakkında Genel Tebliğ.

Bu kayıtları kalıcı doğruluk garantisi sayma; her yeni görevde yeniden kontrol et.
