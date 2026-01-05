import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df = pd.read_excel("clustering_output.xlsx")

    df["Tanggal Penerimaan"] = pd.to_datetime(
        df["Tanggal Penerimaan"], errors="coerce"
    )
    df["bulan"] = df["Tanggal Penerimaan"].dt.to_period("M").astype(str)

    df["dominant_topic"] = df["dominant_topic"].fillna(-1).astype(int)

    topic_map = {
        0: "Pembayaran & Komite Sekolah",
        1: "Administrasi & Informasi Pendidikan",
        2: "PPDB & Sumbangan",
        3: "Pungutan Liar & Ijazah",
        4: "Tunjangan & Bantuan Guru",
        -1: "Topik Tidak Diketahui"
    }

    df["nama_topik"] = df["dominant_topic"].map(topic_map)
    return df

df = load_data()

# ======================
# HEADER
# ======================
st.title("📊 Dashboard Pengaduan Publik Pendidikan")
st.caption("PPID Dinas Pendidikan Provinsi Jawa Timur | Analisis Topik LDA")

# ======================
# FILTER
# ======================
topik = st.multiselect(
    "Pilih Topik",
    options=sorted(df["nama_topik"].unique()),
    default=sorted(df["nama_topik"].unique())
)

bulan = st.multiselect(
    "Pilih Bulan",
    options=sorted(df["bulan"].unique()),
    default=sorted(df["bulan"].unique())
)

df_f = df[
    (df["nama_topik"].isin(topik)) &
    (df["bulan"].isin(bulan))
]

# ======================
# KPI
# ======================
c1, c2, c3 = st.columns(3)

c1.metric("Total Pengaduan", len(df_f))

if not df_f.empty:
    c2.metric("Topik Terbanyak", df_f["nama_topik"].value_counts().idxmax())
    c3.metric(
        "Rata-rata Durasi (hari)",
        round(df_f["Durasi (hari)"].mean(), 2)
    )
else:
    c2.metric("Topik Terbanyak", "N/A")
    c3.metric("Rata-rata Durasi (hari)", "N/A")

# ======================
# DISTRIBUSI TOPIK
# ======================
# Distribusi pengaduan per topik
if not df_f.empty:
    topic_dist = (
        df_f
        .groupby("nama_topik")
        .size()
        .reset_index(name="Jumlah")
    )

    fig1 = px.bar(
        topic_dist,
        x="nama_topik",
        y="Jumlah",
        title="Distribusi Pengaduan Berdasarkan Topik", 
        labels={
        "nama_topik": "Topik",
        "Jumlah": "Jumlah Pengaduan"})
    
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Tidak ada data untuk filter yang dipilih.")


# ======================
# TREN WAKTU
# ======================
if not df_f.empty:

    trend = (
        df_f
        .groupby(["bulan", "nama_topik"])
        .size()
        .reset_index(name="Jumlah")
    )

    # URUTKAN BULAN (WAJIB)
    trend["bulan"] = pd.to_datetime(trend["bulan"])
    trend = trend.sort_values("bulan")
    trend["bulan"] = trend["bulan"].dt.to_period("M").astype(str)

    max_y = st.slider(
        "Batas maksimum sumbu Y",
        min_value=5,
        max_value=100,
        value=20
    )

    fig2 = px.line(
        trend,
        x="bulan",
        y="Jumlah",
        color="nama_topik",
        markers=True,
        title="Tren Pengaduan Publik Pendidikan per Topik",
        labels={
            "bulan": "Bulan",
            "Jumlah": "Jumlah Pengaduan",
            "nama_topik": "Topik"
        }
    )

    fig2.update_yaxes(range=[0, max_y])

    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Tidak ada data untuk ditampilkan pada tren waktu.")


# ======================
# TABEL DETAIL
# ======================
if not df_f.empty:
    st.dataframe(
        df_f[
            [
                "Tanggal Penerimaan",
                "nama_topik",
                "Substansi Masalah",
                "Durasi (hari)"
            ]
        ].rename(columns={
            "nama_topik": "Topik"
        })
    )

