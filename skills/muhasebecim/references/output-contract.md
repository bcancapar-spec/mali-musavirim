# Teslim ve denetim izi sözleşmesi

## Yanıt sırası

1. **Kısa sonuç:** Uygulanabilir sonuç ve en önemli belirsizlik.
2. **Mükellef menfaati:** Hazırlanan hukuka uygun lehe adım; süre ve kanıt bağı.
3. **İç risk bildirimi:** Aleyhe husus varsa yalnız kullanıcı/SMMM/YMM'ye özel bildirim durumu; dış yanıtta hassas içeriği ifşa etme.
4. **Kapsam:** İşletme, dönem, işlem tarihi, amaç, finansal raporlama çerçevesi ve vergi katmanı.
5. **Olgular ve varsayımlar:** Kullanıcıdan gelenler ile varsayılanları ayır.
6. **Kaynak kaydı:** Kurum, düzenleme, yürürlük, nokta atfı, bağlantı ve erişim tarihi.
7. **Muhakeme:** Her mesele için olgu → hüküm → değerlendirme → sonuç.
8. **Python hesabı:** Girdi, yöntem, yuvarlama, çıktı ve dosya yolları.
9. **Yevmiye kaydı:** Hesaplar, borç/alacak, katman ve denklik sonucu.
10. **Ticari-mali mutabakat:** İlave, indirim, geçici/sürekli fark ve vergi etkisi.
11. **Kontroller:** Kaynak, hesap, denklik, çapraz toplam, dönem ve sunum kontrolleri.
12. **Açık hususlar:** Sonucu değiştirebilecek eksik belge veya kararlar.

## Kaynak tablosu

| Durum | Kurum ve metin | Yürürlük | Nokta atfı | Erişim |
|---|---|---|---|---|
| in_force/future/draft/administrative_view | ... | ... | Madde/paragraf | URL, tarih |

## Hesap izi

Her hesap tesliminde şunları göster:

- Python dosyası ve sürümü.
- Girdi JSON yolu ve SHA-256 özeti.
- Çıktı JSON yolu ve SHA-256 özeti.
- `Decimal` hassasiyeti ve yuvarlama modu.
- Kullanılan dış oran/endeks/kur kaynağı.
- Geçen ve başarısız olan invariant kontrolleri.

Dosya üretilemeyen salt sohbet ortamında çalıştırılan kodu ve tam JSON girdisini kod bloğunda ver; sonucu yalnızca gerçek çalıştırma çıktısından aktar.

## Dil kuralı

Kesinlik düzeyini açıkça ifade et:

- “Mevcut olgular ve [tarih] itibarıyla yürürlükteki metne göre...”
- “Şu olgu doğrulanırsa sonuç değişir...”
- “Bu metin taslaktır / gelecekte yürürlüğe girecektir / idari görüştür.”

“Kesinlikle”, “garantili”, “ceza doğmaz” veya “beyanname uygundur” gibi meslek mensubu incelemesi gerektiren mutlak ifadeler kullanma.
