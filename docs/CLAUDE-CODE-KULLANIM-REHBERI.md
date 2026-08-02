# Mali Müşavirim'i Claude Code ile Kullanma Rehberi

Bu rehber, `mali-musavirim` deposunu Claude Code içinde nasıl açacağınızı, proje yeteneklerini nasıl çağıracağınızı, Python motorlarını nasıl çalıştıracağınızı ve hassas mükellef verisi söz konusu olduğunda hangi sınırları korumanız gerektiğini açıklar.

Rehber 2 Ağustos 2026 tarihinde resmî Claude Code dokümantasyonu esas alınarak hazırlanmıştır. Claude Code sık güncellendiği için kurulum, veri kullanımı ve izin ayrıntılarını uygulama tarihinde yeniden kontrol edin.

## 1. Kısa cevap: Claude Code içinde nasıl başlatılır?

Windows PowerShell'de:

```powershell
git clone https://github.com/bcancapar-spec/mali-musavirim.git
Set-Location .\mali-musavirim
claude
```

Claude Code açıldıktan sonra genel muhasebe yeteneğini doğrudan çağırın:

```text
/muhasebecim
Bu projeyi ve kontrol motorlarını incele. Hiçbir dosyayı değiştirmeden test durumunu, desteklenen işlemleri ve mesleki sınırları açıkla.
```

Vergi incelemesine hazırlık için:

```text
/vergi-mufettisi
Sentetik bir mizan ve yevmiye örneği için incelemeye hazırlık kontrol planı oluştur. Kamu yetkisi kullanma ve bütün hesapları Python ile yap.
```

YMM tasdik dosyası için:

```text
/yeminli-mali-musavir
Sentetik bir tam tasdik dosyası için iş kabulü, bağımsızlık, sözleşme, kanıt ve rapor kalite kapılarını çıkar.
```

Depo kökünde başlatılan Claude Code, proje talimatı olan `CLAUDE.md` dosyasını otomatik olarak bağlama alır. `.claude/skills/` altındaki üç yönlendirici sayesinde yukarıdaki yetenekler `/muhasebecim`, `/vergi-mufettisi` ve `/yeminli-mali-musavir` komutları olarak görünür.

## 2. Claude Code bu projeye ne kazandırır?

Claude Code bu depoda bir terminal ve kod çalışma yardımcısıdır. Doğru kullanıldığında:

- proje dosyalarını ve dokümantasyonu açıklar,
- uygun muhasebe uzmanlığını seçer,
- Python motorlarını çalıştırmak için komut hazırlar,
- kullanıcı izniyle kod ve dokümantasyon değişikliği yapar,
- testleri ve katalog denetimlerini çalıştırır,
- deterministik JSON sonuçlarını meslek dilinde açıklar,
- `BLOCK` ve uyarıları ilgili kural kimliği ve kanıtıyla sunar,
- mükellef lehine hukuka uygun adımı ve aleyhe durum için iç bildirim taslağını hazırlar.

Claude Code'un kendisi muhasebe motoru değildir. Sayısal doğruluğun kaynağı, depodaki çalıştırılabilir Python kodu ve deterministik kural motorlarıdır. Modelin metinsel cevabı, Python hesap izi ve kaynak kanıtı olmadan yeterli kabul edilmez.

## 3. Kurulum

### 3.1 Sistem ihtiyaçları

Bu proje için gerekenler:

- Git,
- Python 3.11 veya daha yeni bir sürüm,
- Claude Code,
- Claude Code kullanımına uygun hesap veya desteklenen kurumsal model sağlayıcısı,
- kurulum ve model iletişimi için internet bağlantısı.

Claude Code'un güncel resmî gereksinimleri ve platform seçenekleri için [Claude Code gelişmiş kurulum rehberini](https://code.claude.com/docs/en/getting-started) kontrol edin.

### 3.2 Windows kurulumu

Resmî belgelerde önerilen yerel PowerShell kurulumu:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Alternatif WinGet kurulumu:

```powershell
winget install Anthropic.ClaudeCode
```

Kurulumu kontrol edin:

```powershell
claude --version
claude doctor
```

Claude Code Windows'ta doğrudan PowerShell ile çalışabilir. Git for Windows kurulursa Bash aracından da yararlanabilir. Gerçek ve hassas veriler için işletim sistemi seviyesinde komut izolasyonu gerekiyorsa, resmî belgelere göre WSL 2 yerel Windows'a göre daha uygun seçenektir; Claude Code sandbox'ı yerel Windows'ta desteklenmez.

### 3.3 macOS, Linux veya WSL kurulumu

Resmî yerel kurulum:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Ardından:

```bash
claude --version
claude doctor
```

Kurulum komutları zamanla değişebileceği için kopyalamadan önce resmî sayfayı kontrol edin. `--dangerously-skip-permissions` seçeneğini bu proje için kullanmayın.

### 3.4 Depoyu alma

```powershell
git clone https://github.com/bcancapar-spec/mali-musavirim.git
Set-Location .\mali-musavirim
git status
```

Claude Code'u daima depo kökünde başlatın:

```powershell
claude
```

Alt dizinde başlatmak bazı proje dosyalarının ve yeteneklerin keşfini zorlaştırabilir. Kök dizin, `README.md`, `CLAUDE.md`, `.claude/skills/`, `skills/`, `manifests/` ve testlerin tamamını tek proje bağlamında tutar.

### 3.5 Python ortamı

Temel motorların üçüncü taraf zorunlu bağımlılığı yoktur. Ayrı bir sanal ortam kullanmak isterseniz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[pdf,spreadsheets]"
```

PDF ve elektronik tablo desteği gerekmiyorsa son komutta yalnızca `-e .` kullanabilirsiniz.

## 4. Depodaki Claude Code uyumluluk katmanı

### 4.1 `CLAUDE.md`

Depo kökündeki `CLAUDE.md`, her Claude Code oturumuna uygulanacak kısa ve ortak proje kurallarını içerir:

- bütün hesapların Python ile yapılması,
- `Decimal` kullanımı,
- finansal raporlama ve vergi katmanının ayrılması,
- resmî kaynak ve vaka tarihi kontrolü,
- deterministik `BLOCK` sonucunun atlanmaması,
- mükellef lehine adım ve aleyhe iç bildirim,
- hassas verinin model bağlamına alınmaması,
- test ve teslim kalite kapıları.

Claude Code'un proje `CLAUDE.md` dosyasını nasıl yüklediği [resmî proje belleği belgesinde](https://code.claude.com/docs/en/memory) açıklanmaktadır.

Oturum içinde yüklenen talimatları kontrol etmek için:

```text
/memory
```

Listede depo kökündeki `CLAUDE.md` görünmelidir.

### 4.2 Claude Code yetenekleri

Claude Code proje yeteneklerini `.claude/skills/<yetenek>/SKILL.md` konumundan keşfeder. Bu depoda üç yönlendirici bulunur:

| Claude Code komutu | Kanonik yetenek | Kullanım alanı |
|---|---|---|
| `/muhasebecim` | `skills/muhasebecim/SKILL.md` | Genel muhasebe, THP/VUK, standartlar, ingest ve Python hesapları |
| `/vergi-mufettisi` | `skills/vergi-mufettisi/SKILL.md` | Vergi incelemesine hazırlık, risk ve kanıt zinciri |
| `/yeminli-mali-musavir` | `skills/yeminli-mali-musavir/SKILL.md` | YMM iş kabulü, bağımsızlık, tasdik ve kalite kapıları |

Yönlendirici dosyalar, aynı kuralları ikinci kez kopyalamaz. Claude Code'a kanonik `skills/` dosyasını baştan sona okumasını söyler. Böylece Codex eklentisi ile Claude Code aynı meslek ve hesaplama sözleşmesini kullanır.

Claude Code yeteneklerinin yerleşimi ve `/skill-name` ile çağrılması [resmî Skills belgesinde](https://code.claude.com/docs/en/slash-commands) açıklanır.

## 5. İlk oturumda yapılacak doğrulamalar

Claude Code'u `claude --permission-mode plan` ile açarak salt-okunur bir tanıma turu yapabilirsiniz:

```powershell
claude --permission-mode plan
```

Ardından şu istemi verin:

```text
/muhasebecim
CLAUDE.md ile kanonik muhasebecim yeteneğini okuduğunu doğrula. Dosya değiştirme. Desteklenen 14 Python işlemini, üç deterministik motoru, vaka kapanış kapılarını ve mesleki yetki sınırını dosya yollarıyla özetle.
```

Beklenen davranış:

1. Claude Code `CLAUDE.md` dosyasını proje talimatı olarak tanır.
2. `/muhasebecim` yönlendiricisini yükler.
3. `skills/muhasebecim/SKILL.md` dosyasını okur.
4. Bu aşamada dosya değiştirmez.
5. Hesap sonucunu tahmin etmek yerine motorların nasıl çalıştığını açıklar.

## 6. Testleri Claude Code ile çalıştırma

Claude Code içinde:

```text
/muhasebecim
Test paketini çalıştır. Test sayısını Python raporlayıcısıyla yeniden üret. Başarısız test varsa düzeltme yapmadan önce kök nedeni açıkla.
```

Claude Code'un çalıştırması gereken komutlar:

```powershell
python -m unittest discover -s .\skills\muhasebecim\scripts -p "test_*.py" -v
python .\skills\muhasebecim\scripts\test_suite_report.py
```

Mevcut yayın tabanı `76/76 PASS` sonucudur. Bu sayının dördü Claude Code uyumluluk katmanını doğrular. Gelecekte yeni test eklenirse sayının artması normaldir; sabit bir sayıyı zorlamak yerine keşfedilen, çalıştırılan, geçen ve başarısız olan testleri ayrı ayrı kontrol edin.

## 7. Temel kullanım senaryoları

### 7.1 Projeyi bir mali müşavire açıklatma

```text
/muhasebecim
Bu sistemi bir SMMM'ye yazılımı çalıştırmadan anlat. Belge kabulü, THP/VUK kontrolü, Python hesap izi, mükellef menfaati, iç bildirim ve insan incelemesi zincirini kurgusal bir vaka üzerinden açıkla.
```

### 7.2 Hesap motorundaki işlemleri görme

```text
/muhasebecim
Hesap motorunun desteklediği işlemleri Python komutuyla listele. Her işlemin girdisini, çıktısını ve hangi muhasebe sorusuna cevap verdiğini kısaca açıkla.
```

Motor komutları:

```powershell
python .\skills\muhasebecim\scripts\muhasebecim_engine.py --list
python .\skills\muhasebecim\scripts\muhasebecim_engine.py vat --example
```

### 7.3 Sentetik bir yevmiye kaydını kontrol etme

Gerçek müşteri verisi yerine sentetik veri kullanarak:

```text
/muhasebecim
Tamamen sentetik bir mal alış fişi oluştur. Tutarları JSON dizgesi olarak yaz. KDV ayrıştırmasını ve yevmiye denkliğini Python ile hesapla; sonra THP/VUK journal-validate kapısını çalıştır. Girdi, kod, çıktı ve makbuz yollarını ver.
```

Doğru sonuçta:

- tutarlar `Decimal` esasıyla işlenir,
- borç ve alacak denkliği Python tarafından doğrulanır,
- hesap kodu/adı ve VUK biçim kapıları çalışır,
- sonuç JSON'unda bulgu kimlikleri ve `receipt_sha256` bulunur,
- `PASS` yalnızca tanımlı mekanik kapıların geçtiğini ifade eder.

### 7.4 Yeni vaka açma

Yalnızca sentetik veya onaylı veriyle:

```text
/muhasebecim
2026-12-31 tarihli "ornek-vaka" adında sentetik bir vaka aç. Vaka dosyasının yapısını açıkla ve henüz sağlanmayan kapanış kanıtlarını listele. Eksik kanıtları uydurma.
```

Komut:

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py init `
  --case .\cases\ornek-vaka `
  --case-id ornek-vaka `
  --as-of 2026-12-31
```

Kontrol ve son kapı:

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py check `
  --case .\cases\ornek-vaka

python .\skills\muhasebecim\scripts\case_workflow.py finalize `
  --case .\cases\ornek-vaka
```

`finalize` komutunun başarısız olması her zaman yazılım hatası değildir. Eksik kaynak, hesap izi, THP/VUK sonucu, mükellef lehine fiziksel çalışma kâğıdı, aleyhe iç bildirim veya insan görülme kaydı nedeniyle bilinçli olarak fail-closed davranabilir.

### 7.5 THP/VUK kontrolü

```text
/muhasebecim
THP kataloğunu denetle. Ardından sentetik yevmiye örneğini journal-validate ile çalıştır. BLOCK bulursan kural kimliğini, dayanağını ve düzeltme için gereken olguyu açıkla; sonucu geçersiz kılma.
```

```powershell
python .\skills\muhasebecim\scripts\thp_rule_engine.py catalog-audit
python .\skills\muhasebecim\scripts\thp_rule_engine.py journal-validate `
  --example --output .\journal-example.json
python .\skills\muhasebecim\scripts\thp_rule_engine.py journal-validate `
  --input .\journal-example.json --output .\journal-result.json
```

Genel katalog; banka, sigorta, katılım finans, finansal kiralama, faktoring ve sermaye piyasası gibi sektörel hesap planına tabi işletmelere otomatik uygunluk vermez.

### 7.6 Vergi incelemesine hazırlık

```text
/vergi-mufettisi
Sentetik vaka için vergi incelemesine hazırlık dosyası kur. Risk hipotezlerini olgudan ayır; defter-belge-beyanname mutabakatını Python ile yap; lehe ve aleyhe kanıtı birlikte göster; mükellef haklarını ve açık eksikleri yaz.
```

Motor örneği:

```powershell
python .\skills\muhasebecim\scripts\professional_role_engine.py `
  inspection-readiness-validate --example `
  --output .\inspection-readiness.json
```

Bu mod vergi müfettişi ataması, kamu yetkisi, resmî tutanak veya inceleme raporu üretmez. Yetkili inceleme desteği iddiası için gerçek görevlendirme ve rol kanıtı gerekir.

### 7.7 YMM tasdik dosyasına hazırlık

```text
/yeminli-mali-musavir
Sentetik bir tam tasdik vakasında iş kabulü, ruhsat, sözleşme, bağımsızlık, akrabalık engeli, kanıt, karşıt inceleme ve rapor kalite kapılarını çalıştır. Eksik kanıtı BLOCK olarak koru.
```

```powershell
python .\skills\muhasebecim\scripts\professional_role_engine.py `
  ymm-certification-validate --example `
  --output .\ymm-certification.json
```

Bu mod YMM ruhsatı, bağımsızlık kararı, imza, mühür veya tasdik sonucu üretmez; dosyayı yetkili YMM incelemesine hazırlar.

### 7.8 Mükellef menfaati ve iç bildirim

```text
/muhasebecim
Sentetik vakada hukuka uygun en az bir mükellef lehine adım hazırla. Mükellef aleyhine her olguyu ayrı yerel iç bildirim yap; kullanıcı/SMMM/YMM alıcısını ve görülme durumunu kaydet. Aleyhe olguyu dış taslaktan silerek gizleme.
```

```powershell
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py `
  taxpayer-interest-validate --example `
  --output .\taxpayer-interest.json
```

Lehe adım, hukuka aykırı vergi kaçınma yolu değildir. Doğru kayıt, zorunlu beyan, gerçek kanıt ve mesleki bağımsızlık korunur.

## 8. Hassas mükellef verisi: en önemli sınır

### 8.1 “Yerel Python hesabı” ile “yerel model” aynı şey değildir

Bu deponun Python motorları dosyaları yerel makinede işler; uzak OCR, embedding veya hesaplama servisi kullanmaz. Ancak Claude Code yerel terminalde çalışan, ağ üzerinden bir model sağlayıcısıyla iletişim kuran bir istemcidir.

Resmî Claude Code veri kullanımı belgesine göre istemler ve model çıktıları ağ üzerinden gönderilir. Claude Code'un okuduğu veya kullanıcının sohbete yapıştırdığı müşteri içeriği model bağlamına girebilir. Bu nedenle “dosya diskte yerel duruyor” tek başına gizlilik garantisi değildir.

Güncel veri akışı, eğitim tercihi ve saklama süreleri için [Claude Code Data usage](https://code.claude.com/docs/en/data-usage) sayfasına bakın.

### 8.2 Üç kullanım seviyesi

| Seviye | Veri türü | Claude Code kullanımı |
|---|---|---|
| A — Kod geliştirme | Kaynak kod, public mevzuat, sentetik testler | Uygundur; normal proje izinleriyle kullanılabilir |
| B — Maskelenmiş vaka | Kimlik, VKN/TCKN, IBAN, adres, personel ve ticari sırları geri döndürülemez biçimde temizlenmiş veri | Kurum politikası ve insan kontrolüyle kullanılabilir |
| C — Gerçek mükellef kaydı | Ham yevmiye, mizan, fatura, banka, bordro, sözleşme ve kimlik verisi | Varsayılan olarak Claude Code'a okutmayın; önce yazılı yetki ve veri yönetişimi kararı gerekir |

### 8.3 Gerçek veri için güvenli varsayılan iş akışı

Onaylı kurumsal model/veri işleme düzeni yoksa:

1. Ham dosyayı Git deposuna koymayın.
2. Ham dosyayı Claude Code'a `@dosya`, sürükle-bırak, Read, Grep veya sohbet kopyasıyla vermeyin.
3. Deterministik Python komutunu ayrı ve yerel bir terminalde insan olarak çalıştırın.
4. Ham girdi ve ayrıntılı sonucu erişim kontrollü yerel vaka dizininde tutun.
5. Claude Code'a yalnızca kimliksizleştirilmiş, asgari ve geri döndürülemez bir bulgu özeti verin.
6. Meslek mensubu, ham kayıt ile maskelenmiş özetin tutarlılığını kendi ortamında doğrulasın.

Bu yöntemde Claude Code kodu ve yöntemi açıklayabilir; ham mükellef verisini görmez.

### 8.4 Kurumsal olarak gerçek veriye izin verilecekse

En az şu kararlar yazılı olmalıdır:

- veri sorumlusu/veri işleyen rolleri ve hukuki dayanak,
- müşteri sözleşmesi ve gizlilik kapsamı,
- kullanılacak hesap türü ve model sağlayıcısı,
- eğitimde kullanım tercihi,
- saklama süresi ve varsa Zero Data Retention uygunluğu,
- aktarım bölgesi ve alt işleyenler,
- yerel oturum kayıtlarının saklanması ve silinmesi,
- kimlerin hangi vaka dizinine erişebileceği,
- izin ve sandbox politikası,
- ihlal ve geri çekme prosedürü,
- SMMM/YMM tarafından son insan incelemesi.

Resmî belgelere göre tüketici hesaplarında veri kullanım tercihi kullanıcı ayarına bağlıdır. Ticari Team/Enterprise/API kullanımında varsayılan eğitim politikası farklıdır; ancak standart saklama ile sıfır saklama aynı şey değildir. ZDR her hesapta otomatik bulunmaz. Bu nedenle yalnızca “model eğitiminde kullanılmıyor” ifadesine dayanarak ham muhasebe verisi aktarmayın.

### 8.5 Yerel Claude Code oturum kayıtları

Resmî belge, yerel oturum geçmişinin `~/.claude/projects/` altında düz metin olarak tutulabildiğini açıklar. Windows'ta bu yol genellikle `%USERPROFILE%\.claude\projects\` karşılığındadır. Kurumunuz:

- diski şifrelemeli,
- kullanıcı hesabı erişimini sınırlamalı,
- `cleanupPeriodDays` politikasını belirlemeli,
- ayrılan personelin yerel kayıtlarını temizlemeli,
- gerçek veri içeren oturumlarda `/feedback` kullanımını engellemeli veya yönetmelidir.

Claude Code'un yerel kayıtlarını silmek, muhasebe vaka arşivini silmekle aynı işlem değildir. Mesleki saklama yükümlülüğü kapsamındaki özgün dosyalar ayrı, erişim kontrollü arşiv politikasıyla yönetilmelidir.

## 9. İzinler ve sandbox

Claude Code izinleri, modelin ne yapmak istediğinden ayrı bir istemci kontrolüdür. [Resmî izin belgesine](https://code.claude.com/docs/en/permissions) göre salt okuma, komut çalıştırma ve dosya değiştirme farklı izin davranışlarına sahiptir.

Bu proje için önerilen başlangıç:

1. Depoyu tanırken `plan` modu kullanın.
2. Kod değişikliğinde varsayılan izin moduna geçin ve her komutu okuyun.
3. `/permissions` ile kalıcı izinleri denetleyin.
4. `--dangerously-skip-permissions` veya `bypassPermissions` kullanmayın.
5. Müşteri verisini korumak için yalnızca `CLAUDE.md` talimatına güvenmeyin; izin, işletim sistemi erişimi ve kurumsal politika birlikte uygulanmalıdır.

Salt-okunur başlatma:

```powershell
claude --permission-mode plan
```

İzinleri görüntüleme:

```text
/permissions
```

WSL 2, Linux veya macOS'ta komutları işletim sistemi seviyesinde sınırlamak için [Claude Code sandbox belgesini](https://code.claude.com/docs/en/sandboxing) kullanın. Yerel Windows'ta sandbox desteği bulunmadığı için bir ayar dosyasının WSL 2 ile aynı korumayı sağladığını varsaymayın.

`Read(...)` ve `Edit(...)` engelleri Claude Code'un yerleşik dosya araçlarını sınırlar; tek başına alt süreçlerin dosya okumasını engellemez. Resmî dokümana göre alt süreçlerde işletim sistemi seviyesinde engel için desteklenen sandbox gerekir.

## 10. Etkileşimsiz ve otomasyon kullanımı

Claude Code `-p` ile tek istemi çalıştırıp çıkabilir. Bunu yalnızca kaynak kod, public mevzuat ve sentetik veri için kullanın:

```powershell
claude -p "/muhasebecim Test yapısını değişiklik yapmadan açıkla." `
  --output-format json
```

Oturuma devam etmek için:

```powershell
claude --continue
```

Belirli bir oturumu sürdürmek için:

```powershell
claude --resume <oturum-kimligi>
```

Güncel komut ve bayraklar için [Claude Code CLI reference](https://code.claude.com/docs/en/cli-usage) sayfasına bakın. Otomasyon, SMMM/YMM insan incelemesini veya vaka kapanış kapılarını kaldırmaz.

## 11. Claude Code'a verilebilecek iyi istemler

### Kod inceleme

```text
/muhasebecim
thp_rule_engine.py dosyasını deterministik sıralama, fail-closed davranış, Decimal kullanımı, girdi şeması ve receipt_sha256 kararlılığı açısından incele. Yalnızca kanıtlı bulgu yaz; değişiklik yapma.
```

### Yeni test

```text
/muhasebecim
THP/VUK motorunda aynı kanonik girdinin aynı bulgu sırasını ve receipt_sha256 değerini ürettiğini denetleyen bir negatif ve bir deterministik test ekle. Dar testleri ve tam paketi çalıştır; test raporunu güncelle.
```

### Mevzuat güncelleme hazırlığı

```text
/muhasebecim
2026-12-31 tarihi için bu vakada kullanılan değişken oran ve hadleri listele. Değer uydurma. Her biri için doğrulanması gereken birincil resmî kaynak, yürürlük tarihi ve Python girdi alanını çıkar.
```

### Mükellef lehine ancak hukuka uygun seçenek

```text
/muhasebecim
Bu sentetik vakadaki yasal seçenekleri olgu ve koşullarıyla karşılaştır. Her senaryonun sayısal etkisini Python ile hesapla. En yararlı hukuka uygun adımı öner; aleyhe olguları ayrı iç bildirimde eksiksiz göster.
```

## 12. Kötü veya eksik istem örnekleri

Şu istemlerden kaçının:

- “Bu Excel'i oku, vergiyi söyle.”
  - Dönem, işletme türü, çerçeve, veri yetkisi ve teslim tanımlı değildir.
- “Test geçsin diye BLOCK'u kaldır.”
  - Fail-closed kontrolü anlamsızlaştırır.
- “Oranı internetten bul ve koda yaz.”
  - Vaka tarihi, resmî kaynak ve yürürlük kaydı yoktur.
- “Mükellef aleyhine olanları rapordan sil.”
  - Aleyhe olgu iç analizden saklanamaz; doğru yöntem ayrı yerel iç bildirim ve kontrollü dış taslaktır.
- “Bütün izinleri atla ve bitir.”
  - Hassas veri ve depo güvenliği için uygun değildir.

## 13. Sonucun nasıl okunacağı

Claude Code tesliminde şu ayrımı arayın:

1. Olgular: Kullanıcı veya dosya tarafından sağlanan kanıt.
2. Varsayımlar: Eksik olgu nedeniyle kurulan, sonucu etkileyebilecek kabul.
3. Kaynak: Vaka tarihinde geçerli birincil resmî dayanak.
4. Muhakeme: Olgu ile hüküm arasındaki açık bağ.
5. Python hesap izi: Girdi, kod, yuvarlama ve çıktı.
6. Kural motoru sonucu: `PASS`, `PASS_WITH_WARNINGS` veya `BLOCK`.
7. Mükellef lehine adım: Hukuka uygun ve uygulanabilir koruma seçeneği.
8. Aleyhe iç bildirim: Saklanmayan risk, kanıt, alıcı ve görülme kaydı.
9. Açık hususlar: Sonucu değiştirebilecek eksikler.
10. Yetki sınırı: SMMM/YMM incelemesi ve resmî sorumluluğun devam ettiği alan.

Bir model cümlesi ile Python sonucu çelişirse hesap yeniden çalıştırılır; model cümlesi doğruluk kaynağı sayılmaz. Bir kural motoru `BLOCK` verirse Claude Code'un olumlu yorumu bu kararı geçersiz kılmaz.

## 14. Sorun giderme

### `/muhasebecim` görünmüyor

- Claude Code'u depo kökünde başlattığınızı kontrol edin.
- `.claude/skills/muhasebecim/SKILL.md` dosyasının bulunduğunu kontrol edin.
- Claude Code sürümünü `claude --version` ile kontrol edin.
- Oturumu kapatıp depo kökünde yeniden açın.
- `claude doctor` ile ayar hatalarını inceleyin.

### `CLAUDE.md` uygulanmıyor

- `/memory` komutuyla yüklenen proje talimatlarını kontrol edin.
- Aynı veya üst dizindeki başka `CLAUDE.md`/`CLAUDE.local.md` dosyalarında çelişen talimat olup olmadığına bakın.
- Oturumu depo kökünden başlatın.

### Python bulunamıyor

```powershell
python --version
py --version
```

Windows'ta gerekirse komutlarda `python` yerine `py -3.11` veya sanal ortamın tam Python yolunu kullanın.

### Motor `BLOCK` veriyor

`BLOCK`, çoğu durumda amaçlanan davranıştır. Şunları kontrol edin:

- girdi şeması,
- hesap kodu ve adı,
- borç/alacak denkliği,
- VUK kayıt süresi ve tevsik,
- sektörel hesap planı kapsamı,
- fiziksel kanıt dosyası ve SHA-256,
- rol, ruhsat, sözleşme veya bağımsızlık kanıtı,
- iç bildirimin alıcı ve görülme kaydı.

Kuralı silmek yerine eksik olguyu veya hatalı girdiyi düzeltin.

### Gerçek müşteri dosyası yanlışlıkla depo dizinine kondu

1. Dosyayı Claude Code'a okutmayın.
2. Git durumunu insan olarak kontrol edin.
3. Dosya Git'e eklenmediyse erişim kontrollü yerel vaka alanına taşıyın.
4. Commit veya push yapıldıysa bunu yalnızca dosyayı silmekle çözülmüş saymayın; Git geçmişi, GitHub önbelleği, erişim kayıtları ve olası veri ihlali prosedürünü yetkili kişiyle yönetin.

## 15. Mesleki sorumluluk

Claude Code ile kullanım aşağıdaki yetkileri oluşturmaz:

- SMMM veya YMM ruhsatı,
- beyanname imza ve gönderim yetkisi,
- YMM tasdik ve mühür yetkisi,
- vergi incelemesi veya kamu yetkisi,
- belgenin gerçekliği hakkında kesin karar,
- hukuki veya mali sonucu tek başına kesinleştirme.

Claude Code kodu çalıştırır ve dosyayı meslek mensubu incelemesine hazırlar. Nihai muhasebe kaydı, beyan, tasdik, görüş ve dış gönderim yetkili insan tarafından onaylanır.

## 16. Resmî Claude Code kaynakları

- [Kurulum ve sistem gereksinimleri](https://code.claude.com/docs/en/getting-started)
- [Proje belleği ve CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Skills ve slash komutları](https://code.claude.com/docs/en/slash-commands)
- [CLI komutları ve bayraklar](https://code.claude.com/docs/en/cli-usage)
- [İzin sistemi](https://code.claude.com/docs/en/permissions)
- [Sandbox](https://code.claude.com/docs/en/sandboxing)
- [Veri kullanımı ve saklama](https://code.claude.com/docs/en/data-usage)

Bu kaynaklar Claude Code'un teknik davranışını açıklar. Türk vergi ve muhasebe sonucu için bu deponun sürümlü birincil mevzuat kaynakları ve vaka tarihindeki resmî metinler esas alınır.
