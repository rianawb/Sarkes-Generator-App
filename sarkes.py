import streamlit as st
import pandas as pd
import io
import re

# ==========================================
# 1. KONFIGURASI HALAMAN & DATABASE
# ==========================================

# Menambahkan page_icon (ikon tab browser)
st.set_page_config(
    page_title="Sarkes Generator", 
    layout="wide", 
    page_icon="🏥"
)

# Tambahkan Sidebar Logo
with st.sidebar:
    st.header("🏥 dr. Hayyu")
    st.markdown("Sistem Rekap MCU")
    st.markdown("---")

# CSS Custom untuk Tombol & Tampilan
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #009b54;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #4ed60e;
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

csv_data = """KATEGORI,JENIS PEMERIKSAAN,KODE,BATAS NILAI/PARAMETER,KESIMPULAN,SARAN KHUSUS
FISIK,Nadi,Taki,>100,Takikardia (nadi [XXX] kali/menit),Lakukan pemeriksaan EKG dan konsultasi dengan dokter spesialis jantung jika ada keluhan berdebar-debar atau nyeri dada
FISIK,Nadi,Bradi,<60,Bradikardia (nadi [XX] kali/menit),"Lakukan pemeriksaan EKG dan konsultasi dengan dokter spesialis jantung jika ada keluhan berdebar-debar, pingsan atau nyeri dada"
FISIK,Tekanan Darah,PreHT,120-139/80-89,Prehipertensi (tekanan darah [XXX/XX] mmHg),Monitor tekanan darah secara berkala
FISIK,Tekanan Darah,HT1,140-159/90-100,Hipertensi stage 1 (tekanan darah [XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala
FISIK,Tekanan Darah,HT2,>=160/>=100,Hipertensi stage 2 (tekanan darah [XXX/XXX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala
FISIK,Tekanan Darah,RHT TK,>=140/>=90,Riwayat hipertensi tidak terkontrol (tekanan darah saat ini [XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala
FISIK,Tekanan Darah,RHT Kontrol,<=140/<=90,Riwayat hipertensi terkontrol (tekanan darah saat ini [XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala
FISIK,Indeks Massa Tubuh,Sentral,">=25.0, LP >=80","Obesitas sentral (IMT [XX.X] kg/m2, lingkar perut [YY] cm)",Turunkan BB hingga BB ideal
FISIK,Indeks Massa Tubuh,Obes,>=25.0,Obesitas (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal
FISIK,Indeks Massa Tubuh,Over,23.0-24.9,Overweight (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal
FISIK,Indeks Massa Tubuh,Under,<18.5,Underweight (IMT [XX.X] kg/m2),"Tingkatkan asupan protein dan olahraga secara teratur (3-5x/minggu, minimal 30 menit) untuk meningkatkan massa otot"
FISIK,Visus,[OD; OS; ODS] Miop,TKM,"[OD; OS; ODS] Miopia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Miop,DKM,"[OD; OS; ODS] Miopia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Miop,Koreksi,"[OD; OS; ODS] Miopia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada
FISIK,Visus,[OD; OS; ODS] Hiper,TKM,"[OD; OS; ODS] Hipermetropia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Hiper,DKM,"[OD; OS; ODS] Hipermetropia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Hiper,Koreksi,"[OD; OS; ODS] Hipermetropia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada
FISIK,Visus,[OD; OS; ODS] Pres,TKM,"[OD; OS; ODS] Presbiopia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Pres,DKM,"[OD; OS; ODS] Presbiopia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai
FISIK,Visus,[OD; OS; ODS] Pres,Koreksi,"[OD; OS; ODS] Presbiopia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada
FISIK,Pterigium,[OD; OS; ODS] PTR,Grade 1-3,Pterigium grade [G] di [OD; OS; ODS] ,"Gunakan pelindung mata/kacamata hitam saat beraktivitas di luar ruangan untuk menghindari paparan debu, angin dan sinar matahari"
FISIK,Buta Warna,BW,Parsial,Buta warna parsial,Dapat ditempatkan pada pekerjaan yang tidak membutuhkan ketelitian warna
FISIK,Telinga,Serumen [AD; AS; ADS],,Serumen di [AD; AS; ADS],Konsultasi dengan dokter spesialis THT untuk pembersihan/evakuasi serumen di [AD; AS; ADS]
FISIK,Telinga,Prop [AD; AS; ADS],,Serumen prop di [AD; AS; ADS],
FISIK,Telinga,HL [AD; AS; ADS],,Kesan penurunan pendengaran di [AD; AS; ADS],Lakukan pemeriksaan audiometri dan konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait kesan penurunan pendengaran di [AD; AS; ADS]
FISIK,Tonsil,Tonsil,Ukuran T2/T2; T3/T3; T4/T4,Hipertrofi tonsil [TT/TT],Konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait pembesaran/hipertrofi tonsil
FISIK,Faring,Faring,Hiperemis,Faring hiperemis,Konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan faringitis
FISIK,Mammae,MM [D; S; DS],,Benjolan di payudara [D; S; DS],Konsultasi dengan dokter spesialis bedah onkologi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan benjolan di payudara [D; S; DS]
FISIK,Thoraks,Jantung,Bising,Terdapat bising jantung,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan jantung abnormal
FISIK,Thoraks,Paru,Wheezing,Terdapat wheezing pada paru,Konsultasi dengan dokter spesialis paru untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan paru abnormal
FISIK,Abdomen,NT,Epi,Nyeri tekan epigastrium,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait nyeri tekan epigastrium
FISIK,Abdomen,Ketok [D; S; DS],,Nyeri ketok ginjal [D; S; DS],Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait nyeri ketok ginjal [D; S; DS]
FISIK,Genital perianal,HI,Grade 1-4,Hemorrhoid interna grade [G],"Tingkatkan asupan serat (sayur dan buah), minum air putih minimal 2L/hari dan hindari aktivitas duduk terlalu lama - Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan hemorroid interna"
FISIK,Genital perianal,HE,Eksterna,Hemorrhoid eksterna,"Tingkatkan asupan serat (sayur dan buah), minum air putih minimal 2L/hari dan hindari aktivitas duduk terlalu lama - Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan hemorroid eksterna"
FISIK,Ekstremitas,EXT Kaki O,Kaki O,Bentuk kaki O,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan bentuk kaki O
FISIK,Ekstremitas,EXT Kaki X,Kaki X,Bentuk kaki X,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan bentuk kaki X
FISIK,Gigi,Gigi,Jumlah 1-32,"Gigi: Gigi Hilang ([X]), Sisa Akar ([R]), Abrasi ([A]), Karies ([C]), Karang Gigi ([E]), Perawatan Saluran Akar ([M]), Tumpatan ([F]), Impaksi ([I]), Gigi Palsu ([P]), Gigi Patah ([FR])",Konsultasi dengan dokter gigi untuk perawatan gigi
LAB,Hematologi,Poli,HB >16.0,Suspek polisithemia (Hemoglobin [XX.X] g/dL),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek polisitemia
LAB,Hematologi,ANN,HB  <12.0,Anemia normositik normokromik (Hemoglobin [XX.X] g/dL),"Tingkatkan asupan makanan yang mengandung zat besi (sayuran hijau, daging merah, hati), hindari teh dan kopi - Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait anemia"
LAB,Hematologi,ANM,"HB <12.0, MCV <=80.0,  MCH <=26.0","Anemia mikrositik hipokromik (Hemoglobin [XX.X] g/dL, MCV [YY.Y] fL, MCH [ZZ.Z] pg)","Tingkatkan asupan makanan yang mengandung zat besi (sayuran hijau, daging merah, hati), hindari teh dan kopi - Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait anemia"
LAB,Hematologi,Eritro,>5.9,Eritrositosis [X.X] x 10^6/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait eritrositosis
LAB,Hematologi,LKS,>=12.0,Leukositosis [XX.X] x 10^3/uL --> suspek infeksi bakteri,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait leukositosis
LAB,Hematologi,LKT,10.0-11.9,Peningkatan leukosit [XX.X] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan leukosit
LAB,Hematologi,LKP,<4.0,Leukopenia [X.X] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait leukopenia
LAB,Hematologi,Eos,>4.0,Eosinofilia [X.X] %,Hindari faktor pencetus alergi
LAB,Hematologi,LED,>15,Peningkatan LED [XX] mm/jam,Jaga stamina tubuh Anda
LAB,Hematologi,Fraksi HB,Ditemukan,Ditemukan fraksi hemoglobin varian,Lakukan pemeriksaan analisa hemoglobin
LAB,Hematologi,PLT,>=450,Trombositosis [XXX] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait trombositosis
LAB,Glukosa,GDP,100-125,"Hiperglikemia, glukosa puasa [XXX] mg/dL --> suspek prediabetes","Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,GDP,>=126,"Hiperglikemia, glukosa puasa [XXX] mg/dL --> suspek Diabetes Mellitus","Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,GDP,>=130 (RDM),Riwayat Diabetes Mellitus tidak terkontrol (Glukosa puasa saat ini [XXX] mg/dL),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,GDP,<130 (RDM),Riwayat Diabetes Mellitus terkontrol (Glukosa puasa saat ini [XXX] mg/dL),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,HbA1c,5.7-6.4,Peningkatan HbA1c [X.X] % --> suspek prediabetes,"Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,HbA1c,>=6.5,Peningkatan HbA1c [X.X] % --> suspek Diabetes Mellitus,"Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,HbA1c,>=7.0 (RDM),Riwayat Diabetes Mellitus tidak terkontrol (HbA1c saat ini [X.X] %),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Glukosa,HbA1c,<7.0 (RDM),Riwayat Diabetes Mellitus terkontrol (HbA1c saat ini [X.X] %),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat"
LAB,Lipid Profile,TC,200-239,Kolesterol total dalam batas tinggi [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,TC,>=240,Kolesterol total tinggi [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,LDL,100-129,Kolesterol LDL Direk mendekati optimal [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,LDL,130-159,Kolesterol LDL Direk dalam batas tinggi [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,LDL,160-189,Kolesterol LDL Direk tinggi [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,LDL,>=190,Kolesterol LDL Direk sangat tinggi [XXX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,HDL,<40,Kolesterol HDL rendah [XX] mg/dL,Diet rendah lemak
LAB,Lipid Profile,TG,150-199,Trigliserida dalam batas tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat
LAB,Lipid Profile,TG,200-499,Trigliserida tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat
LAB,Lipid Profile,TG,>=500,Trigliserida sangat tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat
LAB,Faal Ginjal,AU,>=5.7,Hiperurisemia [X.X] mg/dL,Diet rendah purin
LAB,Faal Ginjal,Kreat,>0.90,Peningkatan kreatinin [X.XX] mg/dL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan kreatinin
LAB,Faal Ginjal,GGJ,>0.90 (eLFG >=60),"Suspek gangguan fungsi ginjal (Kreatinin [X.XX] mg/dL, eLFG [YY] mL/menit/1.73 m2)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi ginjal
LAB,Faal Ginjal,FGJ,>0.90 (eLFG <60),"Suspek penurunan fungsi ginjal (Kreatinin [X.XX] mg/dL, eLFG [YY] mL/menit/1.73 m2)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek penurunan fungsi ginjal
LAB,Faal hati,Hati GOT,>=27,Peningkatan enzim hati (GOT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati
LAB,Faal hati,Hati GPT,>=34,Peningkatan enzim hati (GPT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati
LAB,Faal hati,Hati ALL,GOT >=27 & GPT >=34,"Peningkatan enzim hati (GOT [XX] U/L, GPT [YY] U/L)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati
LAB,Faal hati,GGH GOT,>=54,Suspek gangguan fungsi hati (GOT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati
LAB,Faal hati,GGH GPT,>=68,Suspek gangguan fungsi hati (GOT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati
LAB,Faal hati,GGH ALL,GOT >=54 & GPT>=68,"Suspek gangguan fungsi hati (GOT [XX] U/L, GPT [YY] U/L)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati
LAB,Faal hati,HBsAg,Reaktif,HBsAg Reaktif,"Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan HBsAg reaktif - Lakukan pemeriksaan imunologi/serologi untuk menentukan status infeksi Hepatitis B"
LAB,Faal hati,AntiHBs,NR,Belum terbentuk antibodi/kekebalan terhadap virus Hepatitis B,Vaksinasi Hepatitis B untuk memberikan kekebalan terhadap virus Hepatitis B
LAB,Faal hati,AntiHBs,Reaktif,Sudah terbentuk antibodi/kekebalan terhadap virus Hepatitis B,
LAB,Mikronutrien,Vit D,<20.0,Defisiensi vitamin D (Vitamin D 25-OH Total [XX.X] ng/mL),"Tingkatkan paparan sinar matahari pagi selama ±5–15 menit setiap hari, terutama pada area tangan dan kaki. Perbanyak konsumsi makanan kaya vitamin D (ikan laut, telur, susu, keju), serta pertimbangkan suplementasi vitamin D sesuai anjuran dokter"
LAB,Mikronutrien,Vit D,>=20.0-29.9,Insufisiensi vitamin D (Vitamin D 25-OH Total [XX.X] ng/mL),"Tingkatkan paparan sinar matahari pagi selama ±5–15 menit setiap hari, terutama pada area tangan dan kaki. Perbanyak konsumsi makanan kaya vitamin D (ikan laut, telur, susu, keju), serta pertimbangkan suplementasi vitamin D sesuai anjuran dokter"
LAB,Urinalisa,Albuminuria,[text_input],Albuminuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Ketonuria,[text_input],Ketonuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Leukosituria,[text_input],"Leukosituria [text_input]/uL, sedimen leukosit [text_input]/LPB",Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Glukosuria,[text_input],Glukosuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Hematuria,[text_input],"Hematuria [text_input]/uL, sedimen eritrosit [text_input]/LPB",Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Kristaluria,,Kristaluria normal amorf urat (+)/LPB,Minum air putih minimal 2L/hari
LAB,Urinalisa,Urobilinogen,[text_input],Urobilinogenuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal
LAB,Urinalisa,Silinder kasar,[text_input],Silinder berbutir kasar [text_input]/LPK,Minum air putih minimal 2L/hari
LAB,Urinalisa,Silinder halus,[text_input],Silinder berbutir halus [text_input]/LPK,Minum air putih minimal 2L/hari
LAB,Urinalisa,Epitel,[text_input],Epitel skuamosa [text_input]/LPK,Minum air putih minimal 2L/hari
LAB,Urinalisa,Bakteriuria,,Bakteriuria (+)/LPB,Hindari kebiasaan menahan BAK dan jaga higienitas area genitalia
LAB,Feses,FS Parasit,Parasit,Ditemukan parasit blastocystis hominis (+) pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal
LAB,Feses,FS Leuko,Leuko,Ditemukan leukosit 0-1/LPB pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal
LAB,Feses,FS Eri,Eri,Ditemukan eritrosit 0-1/LPB pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal
RONTGEN ,Thorax,Ro,Bronchitis,Rontgen Thorax: Bronchitis,Konsultasi dengan dokter spesialis paru untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal
RONTGEN ,Thorax,Ro,Cardiomegali,Rontgen Thorax: Cardiomegali,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal
RONTGEN ,Thorax,Ro,Scoliosis,Rontgen Thorax: Dextroscoliosis thoracalis,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal
AUDIOMETRI,Audiometri,Audio [AD; AS; ADS],[text_input],Audiometri [AD; AS; ADS]: [text_input],"Evaluasi faktor risiko dan etiologi terkait hasil audiometri [AD; AS; ADS] abnormal - Konsul dokter spesialis THT untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil audiometri [AD; AS; ADS] abnormal"
SPIROMETRI,Spirometri,Spiro,Restriksi ringan,Spirometri: Restriksi ringan,Tingkatkan olahraga aerobik
SPIROMETRI,Spirometri,Spiro,Restriksi sedang,Spirometri: Restriksi sedang,"Tingkatkan olahraga aerobik - Konsul dokter spesialis paru untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil spirometri abnormal"
SPIROMETRI,Spirometri,Spiro,Obstruksi ringan,Spirometri: Obstruksi ringan,Tingkatkan olahraga aerobik
SPIROMETRI,Spirometri,Spiro,Obstruksi sedang,Spirometri: Obstruksi sedang,"Tingkatkan olahraga aerobik - Konsul dokter spesialis paru untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil spirometri abnormal"
EKG,EKG,EKG Taki,100-150,EKG: Sinus tachycardia HR [XXX] bpm normoaxis,Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal
EKG,EKG,EKG Bradi,30-59,EKG: Sinus bradycardia HR [XX] bpm normoaxis,Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal
EKG,EKG,EKG RAD,50-99,"EKG: Sinus rhythm HR [XX] bpm, RAD",Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal
EKG,EKG,EKG LAD,50-99,"EKG: Sinus rhythm HR [XX] bpm, LAD",Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal
TREADMILL,Treadmill,TMT,Iskemik,Treadmill test: Respon ischemic positive,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil Treadmill Test abnormal
USG,USG Abdomen,USG Abd,[text_input],USG Whole Abdomen: [text_input],Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil USG Abdomen abnormal
USG,USG Mammae,USG MM,[text_input],USG Mammae: [text_input],Konsultasi dengan dokter spesialis bedah onkologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil USG Mammae abnormal
SSBC,SSBC,SSBC,[text_input],SSBC: [text_input],Konsultasi dengan dokter spesialis obsgyn untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil SSBC abnormal
KONSUL,Konsul Gizi,Konsul Gizi,,,Konsultasi dengan dokter spesialis gizi klinik untuk tata laksana lebih lanjut terkait obesitas
KONSUL,Konsul Dokter,Konsul sppd,[text_input],,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input]
KONSUL,Konsul Dokter,Konsul spog,[text_input],,Konsultasi dengan dokter spesialis obsgyn untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input]
KONSUL,Konsul Dokter,Konsul sps,[text_input],,Konsultasi dengan dokter spesialis saraf untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input]
KONSUL,Konsul Dokter,Konsul spb,[text_input],,Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input]
ANAMNESIS,Keluhan,Keluhan,[text_input],Keluhan saat ini: [text_input],Konsultasi dengan dokter untuk pemeriksaan dan tata laksana lebih lanjut terkait keluhan saat ini
"""

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_db(csv_text):
    # Load sebagai string agar data kosong tidak otomatis jadi NaN (float)
    df = pd.read_csv(io.StringIO(csv_text), dtype=str)
    # Ganti NaN dengan string kosong
    return df.fillna("")

def expand_code_variants(row_code):
    if not row_code: return []
    row_code = str(row_code).strip()
    
    # Cari pola [A; B; C]
    match = re.search(r"\[(.*?)\]", row_code)
    if match:
        options = [opt.strip() for opt in match.group(1).split(";")]
        base = row_code
        expanded = []
        for opt in options:
            # Ganti bagian [A; B] dengan opsi tunggal
            new_code = base.replace(match.group(0), opt)
            # Hilangkan double space
            new_code = " ".join(new_code.split())
            expanded.append(new_code)
        return expanded
    return [row_code]

def check_criteria_match(input_val, criteria):
    """
    Mengecek apakah sisa string (input_val) sesuai kriteria Batas Nilai DB.
    """
    input_val = str(input_val).strip()
    criteria = str(criteria).strip()
    
    # Jika kriteria kosong, anggap match
    if not criteria: return True

    # Support untuk placeholder [text_input] sebagai wildcard
    if "[text_input]" in criteria:
        return True
        
    # --- LOGIKA BARU UNTUK RDM (GDP & HbA1c) ---
    # Jika input mengandung "RDM", maka criteria HARUS mengandung "RDM" juga.
    # Jika input TIDAK mengandung "RDM", maka criteria TIDAK BOLEH mengandung "RDM".
    input_has_rdm = "RDM" in input_val.upper()
    criteria_has_rdm = "RDM" in criteria.upper()
    
    if input_has_rdm != criteria_has_rdm:
        return False
    # ---------------------------------------------

    # 1. Cek Text Match (Case Insensitive)
    if criteria.lower() in input_val.lower():
        return True
        
    # 2. Bypass Khusus
    if "jumlah" in criteria.lower(): 
        return True
    if "/" in criteria: 
        return True 

    # 3. Cek Numeric Logic
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", input_val)
    if not nums: return False
    val = float(nums[0])
    
    try:
        # Range Check (e.g., 100-125)
        if '-' in criteria:
            parts = criteria.split('-')
            if len(parts) == 2:
                low_s = re.findall(r"[-+]?\d*\.\d+|\d+", parts[0])
                high_s = re.findall(r"[-+]?\d*\.\d+|\d+", parts[1])
                if low_s and high_s:
                    return float(low_s[0]) <= val <= float(high_s[0])
        
        # Inequality Check (e.g., >100, <12.0, HB <12.0)
        # Bersihkan string dari karakter non-math (kecuali titik dan operator)
        clean_crit = criteria.upper().replace("HB", "").replace(" ", "")
        
        limit_s = re.findall(r"[-+]?\d*\.\d+|\d+", clean_crit)
        if not limit_s: return False
        limit = float(limit_s[0])
        
        if '>=' in clean_crit: return val >= limit
        elif '<=' in clean_crit: return val <= limit
        elif '>' in clean_crit: return val > limit
        elif '<' in clean_crit: return val < limit
    except:
        pass # Gagal parsing, return False
        
    return False

def find_best_match(input_line, db):
    """
    Mencari baris DB yang paling cocok dengan input line.
    Menggunakan logika: Input harus DIAWALI oleh Kode DB.
    """
    input_line = input_line.strip()
    
    for idx, row in db.iterrows():
        # Dapatkan semua variasi kode untuk baris ini
        code_variants = expand_code_variants(row['KODE'])
        # Sort by length descending agar match yang terpanjang dulu (misal: 'ADS' sebelum 'AD')
        code_variants.sort(key=len, reverse=True)
        
        for code in code_variants:
            # Cek apakah input diawali kode ini
            if input_line.lower().startswith(code.lower()):
                # Ambil sisa string sebagai 'Value'
                remainder = input_line[len(code):].strip()
                
                # Cek apakah 'Value' memenuhi kriteria Parameter
                if check_criteria_match(remainder, row['BATAS NILAI/PARAMETER']):
                    return row, code, remainder
                    
    return None, None, None

def replace_placeholders(text, row_input, matched_code_variant):
    """
    Mengganti placeholder dengan nilai, cerdas konteks (OD/OS, dll).
    """
    if not text: return ""
    processed_text = text
    
    # --- Logic 1: Mata & Telinga Contextual Replacement ---
    if "[OD; OS; ODS]" in processed_text:
        replacement = "Mata"
        if matched_code_variant and "ODS" in matched_code_variant: replacement = "Mata kanan dan kiri"
        elif matched_code_variant and "OD" in matched_code_variant: replacement = "Mata kanan"
        elif matched_code_variant and "OS" in matched_code_variant: replacement = "Mata kiri"
        processed_text = processed_text.replace("[OD; OS; ODS]", replacement)

    if "[AD; AS; ADS]" in processed_text:
        replacement = "Telinga"
        if matched_code_variant and "ADS" in matched_code_variant: replacement = "Telinga kanan dan kiri"
        elif matched_code_variant and "AD" in matched_code_variant: replacement = "Telinga kanan"
        elif matched_code_variant and "AS" in matched_code_variant: replacement = "Telinga kiri"
        processed_text = processed_text.replace("[AD; AS; ADS]", replacement)
        
    if "[D; S; DS]" in processed_text:
        replacement = ""
        # Cek dari input juga karena kadang kode tidak memuat sisi (misal Ketok)
        tokens = row_input.upper().split()
        if "DS" in tokens or (matched_code_variant and "DS" in matched_code_variant): replacement = "kanan dan kiri"
        elif "D" in tokens or (matched_code_variant and "D" in matched_code_variant): replacement = "kanan"
        elif "S" in tokens or (matched_code_variant and "S" in matched_code_variant): replacement = "kiri"
        processed_text = processed_text.replace("[D; S; DS]", replacement)

    # --- Logic: Astigmatisme Check ---
    # Jika input mengandung kata "astig" (case-insensitive), tambahkan "Astigmatisme" di belakang diagnosa.
    if "astig" in row_input.lower():
        processed_text = re.sub(r"\b(Miopia|Hipermetropia|Presbiopia)\b", r"\1 Astigmatisme", processed_text, flags=re.IGNORECASE)

    # --- Logic: Leukosituria & Hematuria (Complex Parsing) ---
    if ("Leukosituria" in text or "Hematuria" in text) and text.count("[text_input]") >= 2:
        clean_input = re.sub(r"^(Leukosituria|Hematuria)\s*", "", row_input, flags=re.IGNORECASE).strip()
        match = re.search(r"^(.*?)(?:,?\s*sedimen\s*)(.*)$", clean_input, re.IGNORECASE)
        if match:
            val1 = match.group(1).strip()
            val2 = match.group(2).strip()
            processed_text = processed_text.replace("[text_input]", val1, 1)
            processed_text = processed_text.replace("[text_input]", val2, 1)
            return processed_text

    # --- Logic 2: Gigi (Parsing Khusus) ---
    if "Gigi: Gigi Hilang" in text:
        clean_input = re.sub(r"^Gigi\s*", "", row_input, flags=re.IGNORECASE).strip()
        segments = [s.strip() for s in clean_input.split(',')]
        dental_map = {}
        for seg in segments:
            parts = seg.split()
            if len(parts) >= 1:
                code = parts[0].upper()
                val = parts[1] if len(parts) > 1 else ""
                dental_map[code] = val
        
        template_parts = [
            ('X', 'Gigi Hilang ([X])'), ('R', 'Sisa Akar ([R])'), ('A', 'Abrasi ([A])'),
            ('C', 'Karies ([C])'), ('E', 'Karang Gigi ([E])'), ('M', 'Perawatan Saluran Akar ([M])'),
            ('F', 'Tumpatan ([F])'), ('I', 'Impaksi ([I])'), ('P', 'Gigi Palsu ([P])'), ('FR', 'Gigi Patah ([FR])')
        ]
        active_items = []
        for code, template_phrase in template_parts:
            if code in dental_map:
                active_items.append(template_phrase.replace(f"[{code}]", dental_map[code]))
        
        if active_items: processed_text = "Gigi: " + ", ".join(active_items)
        else: processed_text = "Gigi: Tidak ada kelainan"
        return processed_text

    # --- Logic 3: Numeric Placeholders ---
    # Modifikasi: Gunakan sisa string setelah kode dibuang untuk mencari angka
    # Hal ini mencegah angka di dalam Kode (misal "HbA1c", "HT1") terambil sebagai nilai result
    search_text = row_input
    if matched_code_variant:
        # Hapus kode di awal string (case insensitive)
        pattern = re.compile(re.escape(matched_code_variant), re.IGNORECASE)
        search_text = pattern.sub("", row_input, count=1)
    
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", search_text)
    
    if "[XXX/XX]" in processed_text and "/" in row_input:
        match = re.search(r"(\d+/\d+)", row_input)
        if match: processed_text = processed_text.replace("[XXX/XX]", match.group(1))
    
    placeholders = re.findall(r"\[[A-Z\.]+\]", processed_text)
    numeric_placeholders = [p for p in placeholders if "OD" not in p and "AD" not in p and "DS" not in p and "text" not in p and "G" not in p]
    
    idx_num = 0
    for ph in numeric_placeholders:
        if ph in processed_text and idx_num < len(numbers):
            if "/" in row_input and ("XXX/XX" in ph): continue 
            processed_text = processed_text.replace(ph, numbers[idx_num], 1)
            idx_num += 1

    # --- Logic 4: Text Input / Sisa ---
    if "[text_input]" in processed_text:
        val = row_input # Default full
        # Coba hapus kode matched (Case Insensitive)
        if matched_code_variant and row_input.lower().startswith(matched_code_variant.lower()):
            val = row_input[len(matched_code_variant):].strip()
        processed_text = processed_text.replace("[text_input]", val)

    # Grade [G] dan Tonsil [TT/TT]
    if "[G]" in processed_text:
        match = re.search(r"Grade\s*(\d+)", row_input, re.IGNORECASE)
        val = match.group(1) if match else (numbers[0] if numbers else "")
        processed_text = processed_text.replace("[G]", val)
        
    if "[TT/TT]" in processed_text:
        match = re.search(r"(T\d+/T\d+)", row_input, re.IGNORECASE)
        val = match.group(1) if match else ""
        processed_text = processed_text.replace("[TT/TT]", val)

    return processed_text

def get_lifestyle_advice(conclusion_text):
    keywords = ["obesitas", "overweight", "prehipertensi", "hipertensi", "prediabetes", "diabetes"]
    con_lower = conclusion_text.lower()
    return any(k in con_lower for k in keywords)

def handle_multi_visus(line, db):
    # Cek apakah ini baris Visus ganda
    # Cari semua pasangan Kode Visus (misal: OS Miop, ODS Pres)
    visus_matches = re.findall(r"\b(OD|OS|ODS)\s+(Miop|Hiper|Pres)\b", line, re.IGNORECASE)
    
    # Cari parameter (TKM/DKM/Koreksi)
    param_match = re.search(r"\b(TKM|DKM|Koreksi)\b", line, re.IGNORECASE)
    
    # Syarat: Minimal 2 kode visus DAN 1 parameter ditemukan
    if len(visus_matches) >= 2 and param_match:
        param = param_match.group(0)
        
        parts_conclusions = []
        collected_advices = []
        suffix = ""
        
        for side, cond in visus_matches:
            # Bikin input sintetis: "OS Miop TKM"
            # Sertakan "astig" jika ada di input asli agar logic di replace_placeholders jalan
            synthetic_input = f"{side} {cond} {param}"
            if "astig" in line.lower():
                synthetic_input += " astig"
            
            # Cari match di DB
            match_row, matched_code, remainder = find_best_match(synthetic_input, db)
            
            if match_row is not None:
                # Proses Kesimpulan
                raw_conc = str(match_row['KESIMPULAN'])
                final_conc = replace_placeholders(raw_conc, synthetic_input, matched_code)
                
                # Split untuk ambil bagian depan (diagnosis) dan belakang (status kacamata)
                # Asumsi format: "Mata kiri Miopia, tanpa kacamata"
                if "," in final_conc:
                    parts = final_conc.split(",", 1)
                    core = parts[0].strip()
                    suffix = parts[1].strip() # Akan overwrite, tapi harusnya sama
                    parts_conclusions.append(core)
                else:
                    parts_conclusions.append(final_conc)
                
                # Proses Saran
                raw_adv = str(match_row['SARAN KHUSUS'])
                final_adv = replace_placeholders(raw_adv, synthetic_input, matched_code)
                if final_adv:
                    collected_advices.append(final_adv)
        
        # Gabungkan Kesimpulan
        if parts_conclusions:
            if suffix:
                merged_conclusion = ", ".join(parts_conclusions) + ", " + suffix
            else:
                merged_conclusion = ", ".join(parts_conclusions)
            
            return merged_conclusion, collected_advices
            
    return None, None

def process_patient_block(block, db):
    lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
    
    # MODIFIKASI: Hanya butuh 2 baris awal (ID & Nama)
    if len(lines) < 2: 
        return "Error: Data pasien tidak lengkap (Minimal: ID dan Nama)."
    
    p_id = lines[0]
    p_name = lines[1]
    
    # MODIFIKASI: Data pemeriksaan dimulai dari baris ke-3 (index 2)
    # Melewati Umur dan Jenis Kelamin
    exam_lines = lines[2:]
    
    conclusions = []
    advices = []
    work_status = "Saran Kesehatan Kerja: Belum diinput"
    needs_lifestyle = False
    
    for line in exam_lines:
        line_clean = line.strip()
        if line_clean.upper() == "FWN":
            work_status = "Saran Kesehatan Kerja: Sehat untuk bekerja dengan catatan"
            continue
        if line_clean.lower().startswith("temporary "):
            desc = re.sub(r"^temporary\s+", "", line_clean, flags=re.IGNORECASE)
            work_status = f"Saran Kesehatan Kerja: Tidak sehat untuk bekerja untuk sementara waktu ({desc})\n*Jika sudah melakukan konsultasi dengan dokter spesialis, mendapat tatalaksana dan hasil evaluasi membaik maka Sehat untuk bekerja dengan catatan"
            continue
            
        # Check for Multi Visus case first
        multi_conc, multi_adv = handle_multi_visus(line, db)
        if multi_conc:
            conclusions.append(multi_conc)
            if multi_adv:
                advices.extend(multi_adv)
            continue

        # Normal matching
        match_row, matched_code, remainder = find_best_match(line, db)
        
        if match_row is not None:
            # Kesimpulan
            raw_conc = str(match_row['KESIMPULAN'])
            final_conc = replace_placeholders(raw_conc, line, matched_code)
            
            # Saran
            raw_adv = str(match_row['SARAN KHUSUS'])
            final_adv = replace_placeholders(raw_adv, line, matched_code)
            
            if final_conc:
                conclusions.append(final_conc)
                if get_lifestyle_advice(final_conc): needs_lifestyle = True
            if final_adv:
                advices.append(final_adv)
        else:
            conclusions.append(line)

    output_str = f"{p_id}\n{p_name}\n\nKesimpulan:\n"
    for c in conclusions: output_str += f"{c}\n"
    
    output_str += "\nSaran:\n"
    final_advices = []
    if needs_lifestyle:
        final_advices.extend(["Jaga pola hidup sehat", "Olahraga secara teratur 3-5x/minggu, minimal 30 menit"])
    
    seen_adv = set(final_advices)
    for adv in advices:
        normalized_adv = adv.replace(" - ", "\n")
        subs = [s.strip().lstrip('-').strip() for s in normalized_adv.split('\n')]
        for sub in subs:
            if sub and sub not in seen_adv:
                final_advices.append(sub)
                seen_adv.add(sub)
                
    for fa in final_advices: output_str += f"{fa}\n"
    
    output_str += f"\n{work_status}"
    return output_str

# ==========================================
# 3. MAIN APP
# ==========================================

st.set_page_config(page_title="Sarkes Generator", layout="wide", page_icon="🏥")

# Tambahkan Sidebar Logo
with st.sidebar:
    st.header("🏥 dr. Hayyu")
    st.markdown("Sistem Rekap MCU")
    st.markdown("---")

# Tambahkan CSS custom untuk tombol
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #009b54;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #4ed60e;
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 Sarkes Generator (Resume MCU)")
st.markdown("""
Aplikasi untuk menyusun Resume Hasil Medical Check Up berdasarkan database. <a href="https://docs.google.com/spreadsheets/d/1VVD2VMYPVzjR9HAtJkdykx4dQZsONfSUPQMowXUTpKQ/edit?usp=sharing" target="_blank">Lihat Database</a>

**Cara Pakai:**

1. Masukkan data pasien di kolom input (Untuk Multi-pasien gunakan pemisah `===PATIENT===`).
2. Klik tombol **Proses**.
""", unsafe_allow_html=True)

# Load DB
try:
    db = load_db(csv_data)
    db.columns = [c.strip() for c in db.columns]
except Exception as e:
    st.error(f"Gagal memuat database: {e}")
    st.stop()

input_text = st.text_area("Input Data Pasien", height=300, placeholder="001\nTony Stark\nJantung Bising\nODS Miop TKM\nFWN")

if st.button("Proses Sarkes"):
    if not input_text.strip():
        st.warning("Mohon isi data pasien.")
    else:
        raw_blocks = input_text.split("===PATIENT===")
        results = [process_patient_block(b, db) for b in raw_blocks if b.strip()]
        st.subheader("Hasil Resume (Sarkes)")
        st.text_area("Output", value="\n\n".join(results), height=400)
        
        # Add the code block for copy all functionality
        st.code("\n\n".join(results), language="markdown")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with 🤍 RianLab</p>", unsafe_allow_html=True)