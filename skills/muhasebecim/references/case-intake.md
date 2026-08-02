# Gerçek muhasebe kaydı kabulü

## Yerel kabul sırası

1. Dosyaları yalnızca ilgili vaka klasörünün `documents/` dizinine kopyala; özgün dosyayı değiştirme.
2. İşletme türü, sektör, dönem, amaç, raporlama çerçevesi, para birimi ve önemlilik tutarını `facts.json` içinde tamamla.
3. Her müşteri dosyasını `scope: case` ve yerel göreli yol kullanan ayrı bir manifestle vaka `corpus/` dizinine al.
4. Ingest denetimini çalıştır; `unsupported`, `low_text` veya `extraction_pending` kayıtlarını çözmeden analize geçme.
5. Kaynak satır sayısı, borç/alacak toplamı, tarih aralığı ve tekil hesap sayısını Python ile profil çıkararak kaydet.
6. VKN/TCKN, IBAN, adres ve çalışan verisini kullanıcıya gösterilen ara çıktılarda maskele.

## Desteklenen girdiler

- CSV, TSV, JSON ve TXT doğrudan yerel metin olarak alınır.
- XLSX/XLSM `openpyxl` ile salt okunur alınır; formüller metin olarak korunur, makro ve formüller çalıştırılmaz.
- Metin katmanlı PDF yerel `pypdf` veya `pdftotext` ile çıkarılır.
- Taranmış PDF yerel OCR yoksa `extraction_pending` kalır.
- Eski `.xls` dosyasını yerelde XLSX veya CSV'ye dönüştürmeden desteklenmiş sayma.

## Tercih edilen yevmiye alanları

`journal_no`, `line_no`, `date`, `account_code`, `account_name`, `description`, `debit`, `credit`, `currency`, `exchange_rate`, `document_type`, `document_no`, `cost_center`

## Tercih edilen mizan alanları

`account_code`, `account_name`, `opening_debit`, `opening_credit`, `period_debit`, `period_credit`, `closing_debit`, `closing_credit`, `currency`

Tarihleri `YYYY-MM-DD`, parasal tutarları nokta ondalık ayırıcılı dizge olarak tercih et. Gelen yerel biçimi Python ile dönüştür; özgün dosyayı koru. Sütun adı veya tarih/ondalık biçimi farklıysa eşlemeyi çalışma kâğıdında açıkça kaydet.

## İlk zorunlu kontroller

- Satır ve dosya hash'i, yinelenen kayıt, boş hesap kodu, geçersiz tarih ve sayısal alan kontrolü.
- Yevmiye fişi ve toplam borç/alacak denkliği.
- Mizan kapanış bakiyesi ile hareketlerin matematiksel bağı.
- Hesap kodu biçimi, normal bakiye yönü ve ters bakiye istisnaları.
- Dönem dışı kayıt, mükerrer belge numarası ve eksik belge bağı.
- Dövizli satırda para birimi, kur tarihi, kur kaynağı ve TL karşılık kontrolü.

Bu kontroller yalnızca veri kalitesi ve muhasebe analizine hazırlık sağlar; beyan, imza veya mesleki onay değildir.
