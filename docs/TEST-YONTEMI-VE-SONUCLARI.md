# Test Yöntemi ve Doğrulama Sonuçları

Bu belge, Mali Müşavirim test sayısının neyi ifade ettiğini, hangi yöntemlerin kullanıldığını ve testlerin hangi sınırlar içinde güvence verdiğini açıklar.

## Güncel doğrulanmış sonuç

| Alan | Sonuç |
|---|---|
| Sürüm | `v0.0.3` |
| Test tarihi | 2 Ağustos 2026 |
| Python ortamı | CPython `3.14.6` |
| Test çatısı | Python standart kütüphanesi `unittest` |
| Keşfedilen test | **72** |
| Çalıştırılan test | **72** |
| Başarılı test | **72** |
| Başarısız test | **0** |
| Hata | **0** |
| Atlanan test | **0** |
| Sonuç | **PASS** |

Bu sayı yalnız test fonksiyonlarının adedi değildir. Testlerin içinde pozitif geçiş, negatif blok, kapalı şema, katalog kurcalama, deterministik tekrar, CLI çıkış kodu, SHA-256 makbuzu ve uçtan uca vaka kapısı kontrolleri bulunur.

## Dosya bazında test sayısı

| Test dosyası | Test sayısı | Ana kapsam |
|---|---:|---|
| `test_muhasebecim.py` | 18 | Hesaplama motoru, yerel ingest, vaka akışı ve standart manifesti |
| `test_professional_role_engine.py` | 12 | Vergi müfettişi ve YMM rol/yetki/bağımsızlık kapıları |
| `test_taxpayer_interest_engine.py` | 13 | Mükellef lehine adım, aleyhe iç bildirim ve fiziksel kanıt kapısı |
| `test_thp_rule_engine.py` | 29 | THP kataloğu, VUK yevmiye kontrolleri, mizan ve sürüm bütünlüğü |
| **Toplam** | **72** | Bütün yerel motorlar ve entegrasyon kapıları |

Test sayıları `unittest` keşif ağacından Python ile sayılmıştır; elle toplanmamıştır.

## Testler nasıl çalıştırılır?

Standart ayrıntılı çalıştırma:

```powershell
python -m unittest discover `
  -s .\skills\muhasebecim\scripts `
  -p "test_*.py" -v
```

Makinece okunabilir test raporu:

```powershell
python .\skills\muhasebecim\scripts\test_suite_report.py
```

Raporu JSON dosyasına yazmak için:

```powershell
python .\skills\muhasebecim\scripts\test_suite_report.py `
  --output .\test-result.json
```

Rapor scripti testleri yeniden keşfeder, gerçek çalıştırma sonucunu alır ve şu alanları üretir:

- keşfedilen ve çalıştırılan test sayısı,
- geçen test sayısı,
- başarısızlık ve hata kimlikleri,
- atlanan ve beklenen başarısız testler,
- Python sürümü ve platform,
- bütün paketin başarı durumu.

## Uygulanan test yöntemleri

### 1. Pozitif geçiş testleri

Geçerli örnek girdinin beklenen `PASS` sonucunu verdiği doğrulanır. Örnekler:

- dengeli yevmiye,
- doğru mizan devri,
- geçerli THP hesabı,
- tamamlanmış inceleme hazırlık dosyası,
- bağımsızlık kapıları geçen YMM hazırlık dosyası,
- güncel lehe adımı ve aleyhe hususu bulunmayan mükellef menfaati dosyası,
- görülmüş ve fiziksel dosyaya bağlanmış aleyhe iç bildirim.

### 2. Negatif ve fail-closed testleri

Eksik veya sakıncalı durumun sessizce geçmemesi doğrulanır. Örnekler:

- bilinmeyen hesap kodu,
- hesap adı uyuşmazlığı,
- 7/A ve 7/B karışması,
- genel THP'nin özel düzenlemeli sektöre uygulanması,
- dengesiz yevmiye veya mizan,
- geç kayıt ve belge/tevsik eksikliği,
- YMM ruhsat, mühür, bağımsızlık veya sözleşme eksikliği,
- yetkisiz vergi müfettişi modu,
- mükellef lehine adım bulunmaması,
- süresi geçmiş tek lehe adım,
- aleyhe hususun bildirilmemesi veya görülmemesi,
- aleyhe olgunun gizlendiğinin beyan edilmesi,
- tarafsızlık/bağımsızlık kontrolünün kaldırılması,
- iç bildirimin dış iletime açılması.

Fail-closed yaklaşımda bilinmeyen veya kanıtlanmayan durum “uygun” sayılmaz; `BLOCK` ya da `ERROR` üretir.

### 3. Kapalı şema ve veri tipi testleri

Motorların beklenmeyen alanları, yanlış veri tiplerini ve hatalı kimlikleri reddettiği doğrulanır.

- JSON parasal değerinde `float` reddi,
- boolean yerine metin verilmesi,
- bilinmeyen kök alan,
- tekrar eden kimlik,
- geçersiz tarih,
- geçersiz SHA-256 biçimi,
- kapalı enum dışında rol veya işlem türü.

Şema hatası ile iş kuralı ihlali ayrılır: şema/sistem hatası çıkış kodu `2`; geçerli girdi üzerindeki iş kuralı bloku çıkış kodu `1` üretir.

### 4. Determinizm testleri

Aynı girdi ve aynı katalog iki kez çalıştırılır. Kanonik JSON çıktılarının bire bir eşit olduğu doğrulanır. Bu kontrol:

- bulgu sırasının değişmemesini,
- aynı kural kimliklerinin değerlendirilmesini,
- aynı girdi ve katalog hash'lerinin kullanılmasını,
- aynı `receipt_sha256` makbuzunun üretilmesini

bekler.

Test, mevzuat yorumunun doğruluğundan ayrı olarak motor davranışının tekrar üretilebilirliğini sınar.

### 5. Katalog bütünlüğü ve kurcalama testleri

THP, profesyonel rol ve mükellef menfaati katalogları için ayrı `catalog-audit` kontrolleri bulunur.

Testler:

- sabitlenmiş katalog SHA-256 değerini,
- zorunlu kural kimliklerini,
- kaynak referanslarının varlığını,
- tekrar eden kaynak/kural bulunmamasını,
- kapalı işlem ve enum kümelerini,
- katalog şemasını

doğrular. Katalogdan bir kural silindiğinde hem hash hem kural kümesi kapısının `BLOCK` vermesi ayrıca sınanır.

### 6. Makbuz ve sonuç kurcalama testleri

Motor sonucundaki bir tutar veya statü test içinde sonradan değiştirilir. `case_workflow.py`, `receipt_sha256` yeniden hesaplandığında farkı tespit etmeli ve vaka kapısını kapatmalıdır.

Bu yöntem yalnız dosyanın değiştiğini gösterir; ilk girilen belgenin ekonomik veya hukuki olarak doğru olduğunu tek başına kanıtlamaz.

### 7. Fiziksel dosya ve SHA-256 testleri

Mükellef lehine adım ile aleyhe iç bildirimde yalnız `prepared: true` beyanı yeterli değildir.

Entegrasyon testi:

1. geçici yerel vaka klasörü oluşturur,
2. lehe adım ve iç bildirim JSON dosyalarını fiziksel olarak yazar,
3. dosya kimliği ile SHA-256 özetini motor sonucuna bağlar,
4. vaka kapısının geçtiğini doğrular,
5. dosya baytlarını değiştirir,
6. hash uyuşmazlığında kapının kapandığını doğrular.

Ayrıca dosyanın vaka dizini dışına çıkamaması ve JSON içindeki `action_id` veya `matter_id` değerinin sonuçla eşleşmesi kontrol edilir.

### 8. CLI çıkış kodu testleri

Her deterministik motor alt süreç olarak gerçekten çalıştırılır:

| Çıkış kodu | Test edilen anlam |
|---:|---|
| `0` | `PASS` veya `PASS_WITH_WARNINGS` |
| `1` | Geçerli girdi üzerinde iş kuralı `BLOCK` sonucu |
| `2` | Şema, katalog veya sistem `ERROR` sonucu |

Standart çıktıdaki JSON ayrıca yeniden ayrıştırılır. Böylece yalnız Python fonksiyonu değil, kullanıcı tarafından çalıştırılan komut satırı sözleşmesi de sınanır.

### 9. Vaka kapanışı entegrasyon testleri

Geçici vaka klasörü başlangıçtan kapanışa kadar yürütülür. Kapsam, kaynak, analiz çalışma kâğıdı, Python hesap sonucu, THP/VUK sonucu, profesyonel rol sonucu ve mükellef menfaati sonucu birlikte değerlendirilir.

Özellikle mükellef menfaati kapısının `case.json` içinde `false` yazılarak kapatılamadığı test edilmiştir.

### 10. Yerel veri ve ingest testleri

Testler müşteri verisinin yerel çalışma sınırını da kapsar:

- vaka kapsamındaki internet adresinin reddedilmesi,
- yerel belge hash'i ve tekrar tespiti,
- maskeleme,
- XLSX formüllerinin korunup çalıştırılmaması,
- yeni doğrulama ve çıkarım sürümü oluşturulması.

Testlerde gerçek müşteri verisi kullanılmaz.

## Testlerin kapsamadığı konular

72 test aşağıdakilere ilişkin garanti değildir:

- Gerçek faturanın veya belgenin sahihliği,
- ekonomik özün nihai mesleki yorumu,
- beyannamenin bütünüyle doğru olduğu,
- vergi veya ceza doğmayacağı,
- işlem tarihinde mevzuatın insan tarafından yanlış seçilmediği,
- bütün muhasebe yazılımlarının özel kolon biçimleri,
- performans/yük testi,
- bağımsız sızma testi,
- resmî kurum sistemleriyle canlı entegrasyon,
- SMMM/YMM imza veya tasdik sorumluluğu.

Gerçek kayıt testinde kolon eşlemesi, işlem tarihi, uygulanan raporlama çerçevesi, sektör hesap planı ve mevzuat yürürlüğü ayrıca doğrulanmalıdır.

## Test sonucu ne anlama gelir?

`72/72 PASS`, kodlanmış kontrollerin tanımlı örnek ve karşı örneklerde beklenen şekilde davrandığını gösterir. Bu sonuç “her muhasebe kaydı doğrudur” demek değildir. Sistem, meslek mensubunun yerini almak yerine onun önündeki mekanik hata, kanıt ve süreç risklerini görünür ve yeniden üretilebilir hâle getirir.
