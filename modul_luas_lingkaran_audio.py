    for _, title in MENU:
        if title in ("Latihan Soal", "Progres dan Hasil Belajar"):
            continue
        done = title in st.session_state.completed
        opened = title in st.session_state.visited
        st.markdown(f"- {'✅ Selesai' if done else ('📖 Dibuka, belum ditandai selesai' if opened else '⚪ Belum dibuka')} — **{title}**")
    seen = len(st.session_state.materi_seen)
    st.caption(f"Bagian Materi Inti yang sudah dilihat: {seen}/{len(MATERI_STEPS)}")

    st.markdown("### Latihan")
    a, b = st.columns(2)
    with a:
        st.markdown("**📝 Pilihan Ganda**")
        st.progress(ms["progress"], text=f"Diperiksa {ms['checked']}/{ms['total']} soal")
        if mc["finished"]:
            st.write(f"Nilai: **{ms['nilai']}/100** • benar pertama {ms['benar']} • salah pertama {ms['salah']}")
        elif ms["checked"]:
            st.write(f"Skor sementara: **{ms['nilai']}/100** (belum selesai)")
        else:
            st.write("Belum dikerjakan.")
    with b:
        st.markdown("**🖊️ Esai**")
        st.progress(ess["progress"], text=f"Dikirim {ess['submitted']}/{ess['total']} soal")
        if ess["submitted"]:
            st.write(f"Nilai otomatis sementara: **{ess['nilai_pertama']}/100** (perlu pemeriksaan guru)")
        else:
            st.write("Belum dikerjakan.")

    mastery = topic_mastery(mc, es)
    st.markdown("### Ringkasan penguasaan materi")
    if mastery:
        for t, v in sorted(mastery.items(), key=lambda x: x[1]):
            st.progress(v / 100, text=f"{TOPICS[t]['label']}: {v}% — {'Menguasai ✅' if v >= KKM else 'Perlu latihan ⚠️'}")
        st.caption("Dihitung dari soal pilihan ganda (percobaan pertama) dan kriteria rubrik esai (pengiriman pertama).")
    else:
        st.info("Kerjakan latihan untuk melihat penguasaan materi.")

    st.markdown("### Bagian yang disarankan untuk dipelajari ulang")
    weak = sorted(((t, v) for t, v in mastery.items() if v < KKM), key=lambda x: x[1])
    render_recommendations([(t, f"Penguasaanmu saat ini {v}%.") for t, v in weak], "prog")

    hist = st.session_state.mc_history, st.session_state.essay_history
    if hist[0] or hist[1]:
        st.markdown("### Riwayat latihan sebelumnya")
        for h in hist[0]:
            st.write(f"📝 Pilihan Ganda ({h['waktu']}): nilai {h['nilai']}, benar pertama {h['benar']}, salah pertama {h['salah']}")
        for h in hist[1]:
            st.write(f"🖊️ Esai ({h['waktu']}): nilai otomatis {h['nilai']}, terbaik {h['terbaik']}")
    st.caption("Data disimpan sementara selama sesi aplikasi. Jika halaman ditutup atau dimuat ulang, data akan hilang.")
    nav_buttons()


# ============================================================
# HALAMAN: REFLEKSI
# ============================================================
def page_refleksi():
    page_header("💭 Refleksi Pembelajaran", "Pikirkan apa yang sudah kamu pahami dan bagian yang masih menantang.")
    r = st.session_state.reflection
    U = ["😊 Sudah paham", "🙂 Cukup paham", "🤔 Masih perlu latihan"]
    H = ["Memahami jari-jari dan diameter", "Memilih nilai π", "Menggunakan rumus luas",
         "Mengubah diameter menjadi jari-jari", "Menyelesaikan soal cerita",
         "Menulis langkah esai", "Tidak ada, semuanya cukup mudah"]
    B = ["Sangat membantu", "Cukup membantu", "Belum membantu"]
    with st.form("reflection_form"):
        understanding = st.radio("1. Seberapa paham kamu tentang luas lingkaran?", U,
                                 index=U.index(r["understanding"]) if r.get("understanding") in U else None)
        hard_part = st.selectbox("2. Bagian mana yang paling menantang?", H,
                                 index=H.index(r["hard_part"]) if r.get("hard_part") in H else None,
                                 placeholder="Pilih salah satu")
        useful = st.radio("3. Apakah gambar dan contoh sehari-hari membantumu?", B,
                          index=B.index(r["useful"]) if r.get("useful") in B else None)
        next_step = st.text_area("4. Apa yang ingin kamu pelajari atau latih lagi?", value=r.get("next_step", ""))
        sub = st.form_submit_button("💾 Simpan Refleksi", type="primary")
    if sub:
        st.session_state.reflection = {"understanding": understanding, "hard_part": hard_part,
                                       "useful": useful, "next_step": next_step}
        if understanding and hard_part and useful:
            mark_complete("Refleksi Pembelajaran")
            st.success("Refleksi tersimpan selama sesi ini. Terima kasih sudah belajar! 🌼")
        else:
            st.warning("Refleksi disimpan, tetapi lengkapi pertanyaan 1–3 agar bagian ini ditandai selesai.")
    r = st.session_state.reflection
    if r:
        st.markdown("### Ringkasan refleksimu")
        st.write(f"**Pemahaman:** {r.get('understanding') or 'Belum diisi'}")
        st.write(f"**Bagian menantang:** {r.get('hard_part') or 'Belum diisi'}")
        st.write(f"**Manfaat gambar:** {r.get('useful') or 'Belum diisi'}")
        if r.get("next_step"):
            st.write(f"**Rencana berikutnya:** {r['next_step']}")
    nav_buttons()


# ============================================================
# ROUTER
# ============================================================
PAGES = {
    "Cover": page_cover, "Identitas": page_identitas, "Menu": page_menu,
    "Capaian Pembelajaran": page_capaian, "Petunjuk Penggunaan LKPD": page_petunjuk,
    "Pengantar Materi": page_pengantar, "Materi Inti": page_materi,
    "Latihan Soal": page_latihan, "Latihan PG": page_mc_play, "Hasil PG": page_mc_hasil,
    "Latihan Esai": page_essay_play, "Hasil Esai": page_essay_hasil,
    "Progres dan Hasil Belajar": page_progres, "Refleksi Pembelajaran": page_refleksi,
}

_screen = st.session_state.screen
if _screen not in PAGES:
    _screen = "Cover"
if _screen not in ("Cover", "Identitas") and not st.session_state.student:
    go("Identitas")
st.session_state.visited.add(SECTION_OF.get(_screen, _screen))
st.markdown(bg_css(_screen), unsafe_allow_html=True)
settings_bar()
PAGES[_screen]()

st.divider()
st.caption(f"Modul pembelajaran interaktif • Luas Lingkaran • Kelas VI SD/MI • {NAMA_SEKOLAH}")
st.caption("Data identitas, jawaban, progres, dan refleksi disimpan sementara selama sesi aplikasi berjalan.")
audio_engine()
