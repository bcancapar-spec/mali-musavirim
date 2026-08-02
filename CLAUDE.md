# Mali Müşavirim — Claude Code proje talimatları

Bu depo, Türk muhasebesi ve mali müşavirlik işleri için yerel Python motorları, sürümlü mevzuat kanıtı ve deterministik kontrol kapıları sağlar. Sonuçlar SMMM/YMM incelemesine hazırlıktır; ruhsat, imza, mühür, tasdik veya resmî karar yerine geçmez.

## Her görevde zorunlu kurallar

- Göreve uygun proje yeteneğini kullan:
  - genel muhasebe, THP/VUK, TMS/TFRS, BOBİ FRS, KÜMİ FRS ve hesaplamalar için `/muhasebecim`,
  - vergi incelemesine hazırlık için `/vergi-mufettisi`,
  - YMM tasdik dosyası için `/yeminli-mali-musavir`.
- Yetenek yönlendiricisinin gösterdiği `skills/<yetenek>/SKILL.md` dosyasını ve yalnızca konuyla ilgili referansları oku.
- Basit toplama dâhil bütün sayısal hesap, tarih, süre, sıralama, gruplama, örnekleme, mutabakat ve veri dönüşümünü çalıştırılan Python 3.11+ koduyla yap.
- Parasal ve oran hesaplarında `float` kullanma; `decimal.Decimal` ve açık yuvarlama kuralı kullan.
- Girdi, çalıştırılan kod, ara adımlar ve makinece okunabilir çıktıdan oluşan hesap izini koru.
- Finansal raporlama ile VUK/vergi sonucunu ayrı katmanlarda incele ve aralarındaki farkı mutabıklaştır.
- Değişken oran, had, kur, endeks, süre ve yürürlük bilgisini sabit kodlama; vaka tarihi için birincil resmî kaynaktan doğrula.
- THP/VUK, profesyonel rol ve mükellef menfaati motorlarındaki `BLOCK` sonucunu atlama veya model yorumuyla geçerli sayma.
- Her vakada hukuka uygun en az bir mükellef lehine adım hazırla. Aleyhe olguyu saklama; yerel iç bildirim, koruma adımı, alıcı ve görülme kaydı oluştur.
- Gerçeğe aykırı kayıt, yanıltıcı beyan, kanıt gizleme veya zorunlu açıklamayı atlama önerme.
- Kullanıcı açıkça istemedikçe commit, push, PR, dış gönderim veya resmî sistem işlemi yapma.

## Hassas veri sınırı

- Claude Code ağ kullanan bir model istemcisidir. Okunan dosya içeriği model bağlamına girebilir; “Python yerelde çalışıyor” ifadesi model bağlamının tamamen yerel olduğu anlamına gelmez.
- Onaylı kurumsal veri işleme düzeni yoksa gerçek mükellef kaydını okuma, arama, özetleme veya sohbete kopyalama. Sentetik ya da geri döndürülemez biçimde maskelenmiş veri kullan.
- `cases/`, `.muhasebecim/` ve müşteri dosya türlerini Git'e ekleme. `.gitignore` korumasını kaldırma.
- Gerçek veri için `docs/CLAUDE-CODE-KULLANIM-REHBERI.md` içindeki veri yönetişimi kapısını uygula. Tereddütte dur ve yetkili kullanıcıdan veri işleme kararı iste.

## Temel komutlar

Test paketi:

```powershell
python -m unittest discover -s .\skills\muhasebecim\scripts -p "test_*.py" -v
python .\skills\muhasebecim\scripts\test_suite_report.py
```

Hesap motoru ve THP/VUK denetimi:

```powershell
python .\skills\muhasebecim\scripts\muhasebecim_engine.py --list
python .\skills\muhasebecim\scripts\thp_rule_engine.py catalog-audit
python .\skills\muhasebecim\scripts\professional_role_engine.py catalog-audit
python .\skills\muhasebecim\scripts\taxpayer_interest_engine.py catalog-audit
```

Vaka döngüsü:

```powershell
python .\skills\muhasebecim\scripts\case_workflow.py init --case .\cases\ornek-vaka --case-id ornek-vaka --as-of YYYY-MM-DD
python .\skills\muhasebecim\scripts\case_workflow.py check --case .\cases\ornek-vaka
python .\skills\muhasebecim\scripts\case_workflow.py finalize --case .\cases\ornek-vaka
```

## Değişiklik kalite kapısı

Kod veya kural değişikliğinden sonra:

1. Etkilenen dar testleri çalıştır.
2. Tam `unittest` paketini çalıştır.
3. `test_suite_report.py` ile test sayısını ve sonucu yeniden üret.
4. JSON ve TOML dosyalarını ayrıştırıp doğrula.
5. `git diff --check` çalıştır ve sadece görev kapsamındaki dosyaları değiştir.

## Teslim biçimi

Önce kısa sonucu ver. Ardından dönem/çerçeve, doğrulanmış kaynaklar, olgu-hüküm-muhakeme-sonuç zinciri, Python hesap izi, yevmiye ve vergi mutabakatı, mükellef lehine adım, aleyhe iç bildirim, kontrol sonuçları ve açık kalan hususları göster. `PASS` sonucunu mesleki onay gibi sunma.
