# Bi
tvf_icerik = oku_m3u(tvf)
selcukk_icerik = oku_m3u(selcukk)
an_icerik = oku_m3u(an)
rnl_icerik = oku_m3u(rnl)
madueke_icerik = oku_m3u(madueke)
liveeventsfilter_icerik = oku_m3u(liveeventsfilter)
cdnlivetv_channels_icerik = oku_m3u(cdnlivetv_channels) # Hata düzeltildi

# Birleştir 
birlesik_icerik = (
    tvf_icerik + 
    selcukk_icerik + 
    an_icerik + 
    rnl_icerik + 
    madueke_icerik + 
    cdnlivetv_channels_icerik + # _icerik takısı eklendi (Hata düzeltildi)
    liveeventsfilter_icerik
)

# Yeni dosyaya yaz
with open(cikis_dosyasi, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n")
    for satir in birlesik_icerik:
        f.write(satir + '\n')

print(f"✅ {cikis_dosyasi} dosyası başarıyla oluşturuldu.")
