# Teslim ve denetim izi sözleşmesi

## Yanıt sırası

1. **Kısa sonuç:** Uygulanabilir sonuç ve en önemli belirsizlik.
2. **Kapsam:** İşletme, dönem, işlem tarihi, amaç, finansal raporlama çerçevesi ve vergi katmanı.
3. **Olgular ve varsayımlar:** Kullanıcıdan gelenler ile varsayılanları ayır.
4. **Kaynak kaydı:** Kurum, düzenleme, yürürlük, nokta atfı, bağlantı ve erişim tarihi.
5. **Muhakeme:** Her mesele için olgu → hüküm → değerlendirme → sonuç.
6. **Python hesabı:** Girdi, yöntem, yuvarlama, çıktı ve dosya yolları.
7. **Yevmiye kaydı:** Hesaplar, borç/alacak, katman ve denklik sonucu.
8. **Ticari-mali mutabakat:** İlave, indirim, geçici/sürekli fark ve vergi etkisi.
9. **Kontroller:** Kaynak, hesap, denklik, çapraz toplam, dönem ve sunum kontrolleri.
10. **Açık hususlar:** Sonucu değiştirebilecek eksik belge veya kararlar.

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
