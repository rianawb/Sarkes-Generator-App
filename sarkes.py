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

csv_data = """KATEGORI,JENIS PEMERIKSAAN,KODE,BATAS NILAI/PARAMETER,KESIMPULAN,SARAN KHUSUS,KESIMPULAN (English),SARAN KHUSUS (English)
FISIK,Nadi,Taki,>100,Takikardia (nadi [XXX] kali/menit),Lakukan pemeriksaan EKG dan konsultasi dengan dokter spesialis jantung jika ada keluhan berdebar-debar atau nyeri dada,Tachycardia (pulse [XXX] bpm),"Perform an ECG evaluation and consult a cardiologist if palpitations or chest pain occur"
FISIK,Nadi,Bradi,<60,Bradikardia (nadi [XX] kali/menit),"Lakukan pemeriksaan EKG dan konsultasi dengan dokter spesialis jantung jika ada keluhan berdebar-debar, pingsan atau nyeri dada",Bradycardia (pulse [XX] bpm),"Perform an ECG evaluation and consult a cardiologist if palpitations, fainting, or chest pain occur"
FISIK,Tekanan Darah,PreHT,120-139/80-89,Prehipertensi ([XXX/XX] mmHg),Monitor tekanan darah secara berkala,Prehypertension ([XXX/XX] mmHg),Monitor blood pressure regularly
FISIK,Tekanan Darah,HT1,140-159/90-100,Hipertensi grade 1 ([XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala,Grade 1 Hypertension ([XXX/XX] mmHg),Take antihypertensive medication and monitor blood pressure regularly
FISIK,Tekanan Darah,HT2,>=160/>=100,Hipertensi grade 2 ([XXX/XXX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala,Grade 2 Hypertension ([XXX/XXX] mmHg),Take antihypertensive medication and monitor blood pressure regularly
FISIK,Tekanan Darah,RHT TK,>=140/>=90,Riwayat hipertensi tidak terkontrol (tekanan darah saat ini [XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala,Uncontrolled hypertension (current blood pressure [XXX/XX] mmHg),Take antihypertensive medication and monitor blood pressure regularly
FISIK,Tekanan Darah,RHT Kontrol,<=140/<=90,Riwayat hipertensi terkontrol (tekanan darah saat ini [XXX/XX] mmHg),Minum obat antihipertensi dan monitor tekanan darah secara berkala,Controlled hypertension (current blood pressure [XXX/XX] mmHg),Take antihypertensive medication and monitor blood pressure regularly
FISIK,Indeks Massa Tubuh,Sentral,">=25.0, LP >=80","Obesitas sentral (IMT [XX.X] kg/m2, lingkar perut [YY] cm)",Turunkan BB hingga BB ideal,"Central obesity (BMI [XX.X] kg/m2, waist circumference [YY] cm)",Reduce body weight to achieve an ideal body weight
FISIK,Indeks Massa Tubuh,Obes,>=25.0,Obesitas (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal,Obesity (BMI [XX.X] kg/m2),Reduce body weight to achieve an ideal body weight
FISIK,Indeks Massa Tubuh,OB1,25.0-29.9,Obesitas grade 1 (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal,Grade 1 Obesity (BMI [XX.X] kg/m2),Reduce body weight to achieve an ideal body weight
FISIK,Indeks Massa Tubuh,OB2,>=30.0,Obesitas grade 2 (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal,Grade 2 Obesity (BMI [XX.X] kg/m2),Reduce body weight to achieve an ideal body weight
FISIK,Indeks Massa Tubuh,Over,23.0-24.9,Overweight (IMT [XX.X] kg/m2),Turunkan BB hingga BB ideal,Overweight (BMI [XX.X] kg/m2),Reduce body weight to achieve an ideal body weight
FISIK,Indeks Massa Tubuh,Under,<18.5,Underweight (IMT [XX.X] kg/m2),"Tingkatkan asupan protein dan olahraga secara teratur (3-5x/minggu, minimal 30 menit) untuk meningkatkan massa otot",Underweight (BMI [XX.X] kg/m2),"Increase body weight to achieve an ideal body weight - Increase protein intake and exercise regularly (3-5x/week, at least 30 minutes) to increase muscle mass"
FISIK,Visus,[OD; OS; ODS] Miop,TKM,"[OD; OS; ODS] Miopia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Myopia in [OD; OS; ODS], without glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Miop,DKM,"[OD; OS; ODS] Miopia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Myopia in [OD; OS; ODS], not optimally corrected with glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Miop,Koreksi,"[OD; OS; ODS] Miopia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada,"Myopia in [OD; OS; ODS], optimally corrected with glasses",Consult an ophthalmologist if there is any visual problem with current glasses
FISIK,Visus,[OD; OS; ODS] Hiper,TKM,"[OD; OS; ODS] Hipermetropia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Hypermetropia in [OD; OS; ODS], without glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Hiper,DKM,"[OD; OS; ODS] Hipermetropia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Hypermetropia in [OD; OS; ODS], not optimally corrected with glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Hiper,Koreksi,"[OD; OS; ODS] Hipermetropia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada,"Hypermetropia in [OD; OS; ODS], optimally corrected with glasses",Consult an ophthalmologist if there is any visual problem with current glasses
FISIK,Visus,[OD; OS; ODS] Pres,TKM,"[OD; OS; ODS] Presbiopia, tanpa kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Presbyopia in [OD; OS; ODS], without glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Pres,DKM,"[OD; OS; ODS] Presbiopia, belum terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata untuk koreksi visus mata dengan kacamata yang sesuai,"Presbyopia in [OD; OS; ODS], not optimally corrected with glasses",Consult an ophthalmologist for visual acuity correction with appropriate glasses
FISIK,Visus,[OD; OS; ODS] Pres,Koreksi,"[OD; OS; ODS] Presbiopia, terkoreksi optimal dengan kacamata",Konsultasi dengan dokter spesialis mata jika ada keluhan penurunan penglihatan dengan kacamata yang sudah ada,"Presbyopia in [OD; OS; ODS], optimally corrected with glasses",Consult an ophthalmologist if there is any visual problem with current glasses
FISIK,Pterigium,[OD; OS; ODS] PTR,Grade 1-3,Pterigium grade [G] di [OD; OS; ODS] ,"Gunakan pelindung mata/kacamata hitam saat beraktivitas di luar ruangan untuk menghindari paparan debu, angin dan sinar matahari",Grade [G] Pterygium in [OD; OS; ODS],"Use eye protection/sunglasses during outdoor activities to avoid exposure to dust, wind, and sunlight"
FISIK,Buta Warna,BW,Parsial,Buta warna parsial,Dapat ditempatkan pada pekerjaan yang tidak membutuhkan ketelitian warna,Partial color blindness,Can be placed in jobs that do not require color discrimination
FISIK,Telinga,Serumen [AD; AS; ADS],,Serumen di [AD; AS; ADS],Konsultasi dengan dokter spesialis THT untuk pembersihan/evakuasi serumen di [AD; AS; ADS],Cerumen in [AD; AS; ADS],Consult an ENT specialist for cerumen evacuation in [AD; AS; ADS]
FISIK,Telinga,Prop [AD; AS; ADS],,Serumen prop di [AD; AS; ADS],Konsultasi dengan dokter spesialis THT untuk pembersihan/evakuasi serumen di [AD; AS; ADS],Cerumen prop in [AD; AS; ADS],Consult an ENT specialist for cerumen evacuation in [AD; AS; ADS]
FISIK,Telinga,HL [AD; AS; ADS],,Kesan penurunan pendengaran di [AD; AS; ADS],Lakukan pemeriksaan audiometri dan konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait kesan penurunan pendengaran di [AD; AS; ADS],Impression of hearing loss in [AD; AS; ADS],Perform audiometry and consult an ENT specialist for further evaluation and management regarding hearing loss in [AD; AS; ADS]
FISIK,Tonsil,Tonsil,Ukuran T2/T2; T3/T3; T4/T4,Hipertrofi tonsil [TT/TT],Konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait pembesaran/hipertrofi tonsil,Tonsillar hypertrophy [TT/TT],Consult an ENT specialist for further evaluation and management of tonsillar hypertrophy
FISIK,Faring,Faring,Hiperemis,Faring hiperemis,Konsultasi dengan dokter spesialis THT untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan faringitis,Pharyngeal hyperemia,Consult an ENT specialist for further evaluation and management of pharyngitis findings
FISIK,Mammae,MM [D; S; DS],,Benjolan di payudara [D; S; DS],Konsultasi dengan dokter spesialis bedah onkologi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan benjolan di payudara [D; S; DS],Lump in [D; S; DS] breast,Consult a surgical oncologist for further evaluation and management of breast lump findings in [D; S; DS] breast
FISIK,Thoraks,Jantung,Bising,Terdapat bising jantung,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan jantung abnormal,Heart murmur,Consult a cardiologist for further evaluation and management of abnormal heart findings
FISIK,Thoraks,Paru,Wheezing,Terdapat wheezing pada paru,Konsultasi dengan dokter spesialis paru untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan paru abnormal,Wheezing in lungs,Consult a pulmonologist for further evaluation and management of abnormal lung findings
FISIK,Abdomen,NT,Epi,Nyeri tekan epigastrium,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait nyeri tekan epigastrium,Epigastric tenderness,Consult an internist for further evaluation and management of epigastric tenderness
FISIK,Abdomen,Ketok [D; S; DS],,Nyeri ketok ginjal [D; S; DS],Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait nyeri ketok ginjal [D; S; DS],[D; S; DS] Costovertebral angle tenderness,Consult an internist for further evaluation and management of [D; S; DS] Costovertebral angle tenderness
FISIK,Genital perianal,HI,Grade 1-4,Hemorrhoid interna grade [G],"Tingkatkan asupan serat (sayur dan buah), minum air putih minimal 2L/hari dan hindari aktivitas duduk terlalu lama - Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan hemorroid interna",Grade [G] Internal hemorrhoid,"Increase fiber intake (vegetables and fruits), drink at least 2L of water/day, and avoid prolonged sitting - Consult a surgeon for further evaluation and management of internal hemorrhoid findings"
FISIK,Genital perianal,HE,Eksterna,Hemorrhoid eksterna,"Tingkatkan asupan serat (sayur dan buah), minum air putih minimal 2L/hari dan hindari aktivitas duduk terlalu lama - Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan hemorroid eksterna",External hemorrhoid,"Increase fiber intake (vegetables and fruits), drink at least 2L of water/day and avoid prolonged sitting - Consult a surgeon for further evaluation and management of external hemorrhoids"
FISIK,Ekstremitas,EXT Kaki O,,Bentuk kaki O,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan bentuk kaki O,O-shaped legs,Consult an orthopedic specialist for further evaluation and management of O-shaped legs
FISIK,Ekstremitas,EXT Kaki X,,Bentuk kaki X,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan bentuk kaki X,X-shaped legs,Consult an orthopedic specialist for further evaluation and management of X-shaped legs
FISIK,Gigi,Gigi,Jumlah 1-32,"Gigi: Gigi Hilang ([X]), Sisa Akar ([R]), Abrasi ([A]), Karies ([C]), Karang Gigi ([E]), Perawatan Saluran Akar ([M]), Tumpatan ([F]), Impaksi ([I]), Gigi Palsu ([P]), Gigi Patah ([FR])",Konsultasi dengan dokter gigi untuk perawatan gigi,"Teeth: Missing teeth ([X]), Root remnant ([R]), Abrasion ([A]), Caries ([C]), Calculus ([E]), Root canal treatment ([M]), Filling ([F]), Impaction ([I]), Denture ([P]), Fractured tooth ([FR])",Consult a dentist for dental treatment
LAB,Hematologi,HB,>=15.0,Peningkatan Hemoglobin [XX.X] g/dL,,Increased Hemoglobin [XX.X] g/dL,
LAB,Hematologi,Poli,HB >16.0,Suspek polisithemia (Hemoglobin [XX.X] g/dL),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek polisitemia,Suspect polycythemia (Hemoglobin [XX.X] g/dL),Consult an internist for further evaluation and management of suspected polycythemia
LAB,Hematologi,ANN,HB  <12.0,Anemia normositik normokromik (Hemoglobin [XX.X] g/dL),"Tingkatkan asupan makanan yang mengandung zat besi (sayuran hijau, daging merah, hati), hindari teh dan kopi - Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait anemia",Normocytic normochromic anemia (Hemoglobin [XX.X] g/dL),"Increase intake of iron-rich foods (green vegetables, red meat, liver), avoid tea and coffee - Consult an internist for further evaluation and management of anemia"
LAB,Hematologi,ANM,"HB <12.0, MCV <=80.0,  MCH <=26.0","Anemia mikrositik hipokromik (Hemoglobin [XX.X] g/dL, MCV [YY.Y] fL, MCH [ZZ.Z] pg)","Tingkatkan asupan makanan yang mengandung zat besi (sayuran hijau, daging merah, hati), hindari teh dan kopi - Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait anemia","Microcytic hypochromic anemia (Hemoglobin [XX.X] g/dL, MCV [YY.Y] fL, MCH [ZZ.Z] pg)","Increase intake of iron-rich foods (green vegetables, red meat, liver), avoid tea and coffee - Consult an internist for further evaluation and management of anemia"
LAB,Hematologi,Eritro,>5.0,Eritrositosis [X.X] x 10^6/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait eritrositosis,Erythrocytosis [X.X] x 10^6/uL,Consult an internist for further evaluation and management of erythrocytosis
LAB,Hematologi,LKS,>=12.0,Leukositosis [XX.X] x 10^3/uL --> suspek infeksi bakteri,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait leukositosis,Leukocytosis [XX.X] x 10^3/uL --> suspected bacterial infection,Consult an internist for further evaluation and management of leukocytosis
LAB,Hematologi,LKT,10.0-11.9,Peningkatan leukosit [XX.X] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan leukosit,Increased leukocytes [XX.X] x 10^3/uL,Consult an internist for further evaluation and management of increased leukocytes
LAB,Hematologi,LKP,<4.0,Leukopenia [X.X] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait leukositosis,Leukopenia [X.X] x 10^3/uL,Consult an internist for further evaluation and management of leukopenia
LAB,Hematologi,Eos,4.0-6.9,Peningkatan eosinofil [X.X] %,Hindari faktor pencetus alergi,Increased eosinophils [X.X] %,Avoid allergy triggers
LAB,Hematologi,Eos,>=7.0,Eosinofilia [X.X] %,"Hindari faktor pencetus alergi - Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait eosinofilia",Eosinophilia [X.X] %,"Avoid allergy triggers - Consult an internist for further evaluation and management of eosinophilia"
LAB,Hematologi,LED,>15,Peningkatan LED [XX] mm/jam,Jaga stamina tubuh Anda,Increased ESR [XX] mm/hour,Maintain your body stamina
LAB,Hematologi,Fraksi HB,,Ditemukan fraksi hemoglobin varian,Lakukan pemeriksaan analisa hemoglobin,A hemoglobin variant fraction was found,Perform hemoglobin analysis
LAB,Hematologi,PLT,<=150,Trombositopenia [XXX] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait trombositopenia,Thrombocytopenia [XXX] x 10^3/uL,Consult an internist for further evaluation and management of thrombocytopenia
LAB,Hematologi,PLT,>=450,Trombositosis [XXX] x 10^3/uL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait trombositosis,Thrombocytosis [XXX] x 10^3/uL,Consult an internist for further evaluation and management of thrombocytosis
LAB,Glukosa,GDP,100-125,"Hiperglikemia, glukosa puasa [XXX] mg/dL --> suspek prediabetes","Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat","Hyperglycemia, fasting glucose [XXX] mg/dL --> suspected prediabetes","Lower blood glucose levels and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,GDP,>=126,"Hiperglikemia, glukosa puasa [XXX] mg/dL --> suspek Diabetes Mellitus","Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat","Hyperglycemia, fasting glucose [XXX] mg/dL --> suspected Diabetes Mellitus","Reduce blood glucose levels and perform HbA1c checks regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,GDP,>=130 (RDM),Riwayat Diabetes Mellitus tidak terkontrol (Glukosa puasa saat ini [XXX] mg/dL),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Uncontrolled Diabetes Mellitus (Current fasting glucose [XXX] mg/dL),"Take antidiabetic medication regularly, monitor blood glucose levels, and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,GDP,<130 (RDM),Riwayat Diabetes Mellitus terkontrol (Glukosa puasa saat ini [XXX] mg/dL),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Controlled Diabetes Mellitus (Current fasting glucose [XXX] mg/dL),"Take antidiabetic medication regularly, monitor blood glucose levels, and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,HbA1c,5.7-6.4,Peningkatan HbA1c [X.X] % --> suspek prediabetes,"Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Increased HbA1c [X.X] % --> suspected prediabetes,"Lower blood glucose levels and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,HbA1c,>=6.5,Peningkatan HbA1c [X.X] % --> suspek Diabetes Mellitus,"Turunkan kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Increased HbA1c [X.X] % --> suspected Diabetes Mellitus,"Reduce blood glucose levels and perform HbA1c checks regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,HbA1c,>=7.0 (RDM),Riwayat Diabetes Mellitus tidak terkontrol (HbA1c saat ini [X.X] %),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Uncontrolled Diabetes Mellitus (Current HbA1c [X.X] %),"Take antidiabetic medication regularly, monitor blood glucose levels, and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Glukosa,HbA1c,<7.0 (RDM),Riwayat Diabetes Mellitus terkontrol (HbA1c saat ini [X.X] %),"Minum obat antidiabetes secara rutin, monitor kadar glukosa darah dan lakukan pemeriksaan HbA1c secara berkala setiap 3 bulan - Diet rendah gula dan karbohidrat",Controlled Diabetes Mellitus (Current HbA1c [X.X] %),"Take antidiabetic medication regularly, monitor blood glucose levels, and perform HbA1c test regularly every 3 months - Low sugar and carbohydrate diet"
LAB,Lipid Profile,TC,200-239,Kolesterol total dalam batas tinggi [XXX] mg/dL,Diet rendah lemak,Borderline high total cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,TC,>=240,Kolesterol total tinggi [XXX] mg/dL,Diet rendah lemak,High total cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,LDL,100-129,Kolesterol LDL Direk mendekati optimal [XXX] mg/dL,Diet rendah lemak,Near-optimal direct LDL cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,LDL,130-159,Kolesterol LDL Direk dalam batas tinggi [XXX] mg/dL,Diet rendah lemak,Borderline high direct LDL cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,LDL,160-189,Kolesterol LDL Direk tinggi [XXX] mg/dL,Diet rendah lemak,High direct LDL cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,LDL,>=190,Kolesterol LDL Direk sangat tinggi [XXX] mg/dL,Diet rendah lemak,Very high direct LDL cholesterol [XXX] mg/dL,Low fat diet
LAB,Lipid Profile,HDL,<40,Kolesterol HDL rendah [XX] mg/dL,Diet rendah lemak,Low HDL cholesterol [XX] mg/dL,Low fat diet
LAB,Lipid Profile,TG,150-199,Trigliserida dalam batas tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat,Borderline high triglycerides [XXX] mg/dL,Low fat and carbohydrate diet
LAB,Lipid Profile,TG,200-499,Trigliserida tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat,High triglycerides [XXX] mg/dL,Low fat and carbohydrate diet
LAB,Lipid Profile,TG,>=500,Trigliserida sangat tinggi [XXX] mg/dL,Diet rendah lemak dan karbohidrat,Very high triglycerides [XXX] mg/dL,Low fat and carbohydrate diet
LAB,Faal Ginjal,AU,>=5.7,Hiperurisemia [X.X] mg/dL,Diet rendah purin,Hyperuricemia [X.X] mg/dL,Low purine diet
LAB,Faal Ginjal,Kreat,>0.90,Peningkatan kreatinin [X.XX] mg/dL,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan kreatinin,Elevated creatinine [X.XX] mg/dL,Consult an internist for further evaluation and management of increased creatinine
LAB,Faal Ginjal,GGJ,>0.90 (eLFG >=60),"Suspek gangguan fungsi ginjal (Kreatinin [X.XX] mg/dL, eLFG [YY] mL/menit/1.73 m2)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi ginjal,"Suspected renal function impairment (Creatinine [X.XX] mg/dL, eGFR [YY] mL/min/1.73 m2)",Consult an internist for further evaluation and management of suspected renal function impairment
LAB,Faal Ginjal,FGJ,>0.90 (eLFG <60),"Suspek penurunan fungsi ginjal (Kreatinin [X.XX] mg/dL, eLFG [YY] mL/menit/1.73 m2)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek penurunan fungsi ginjal,"Suspected decreased renal function (Creatinine [X.XX] mg/dL, eGFR [YY] mL/min/1.73 m2)",Consult an internist for further evaluation and management of suspected decreased renal function
LAB,Faal hati,Hati GOT,>=27,Peningkatan enzim hati (GOT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati,Elevated liver enzymes (GOT [XX] U/L),Consult an internist for further evaluation and management of increased liver enzymes
LAB,Faal hati,Hati GPT,>=34,Peningkatan enzim hati (GPT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati,Elevated liver enzymes (GPT [XX] U/L),Consult an internist for further evaluation and management of increased liver enzymes
LAB,Faal hati,Hati ALL,GOT >=27 & GPT >=34,"Peningkatan enzim hati (GOT [XX] U/L, GPT [YY] U/L)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan enzim hati,"Elevated liver enzymes (GOT [XX] U/L, GPT [YY] U/L)",Consult an internist for further evaluation and management of increased liver enzymes
LAB,Faal hati,GGH GOT,>=54,Suspek gangguan fungsi hati (GOT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati,Suspected liver function impairment (GOT [XX] U/L),Consult an internist for further evaluation and management of suspected liver function impairment
LAB,Faal hati,GGH GPT,>=68,Suspek gangguan fungsi hati (GPT [XX] U/L),Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati,Suspected liver function impairment (GPT [XX] U/L),Consult an internist for further evaluation and management of suspected liver function impairment
LAB,Faal hati,GGH ALL,GOT >=54 & GPT>=68,"Suspek gangguan fungsi hati (GOT [XX] U/L, GPT [YY] U/L)",Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek gangguan fungsi hati,"Suspected liver function impairment (GOT [XX] U/L, GPT [YY] U/L)",Consult an internist for further evaluation and management of suspected liver function impairment
LAB,Faal hati,GGT,>60,Peningkatan Gamma GT [XXX] U/L,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait suspek sumbatan saluran empedu,Elevated Gamma GT [XXX] U/L,Consult an internist for further evaluation and management of suspected biliary obstruction
LAB,Faal hati,HBsAg,Reaktif,HBsAg Reaktif,"Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan HBsAg reaktif - Lakukan pemeriksaan imunologi/serologi untuk menentukan status infeksi Hepatitis B",HBsAg Reactive,"Consult an internist for further evaluation and management of reactive HBsAg findings - Perform immunology/serology tests to determine Hepatitis B infection status"
LAB,Faal hati,AntiHBs,NR,Belum pernah terpapar dan belum memiliki kekebalan/antibodi terhadap virus Hepatitis B,Vaksinasi Hepatitis B untuk memberikan kekebalan terhadap virus Hepatitis B,Has not been exposed and does not have immunity/antibodies to Hepatitis B virus,Hepatitis B vaccination to provide immunity against Hepatitis B virus
LAB,Faal hati,AntiHBs,Reaktif,Sudah terbentuk antibodi/kekebalan terhadap virus Hepatitis B,,Has immunity/antibody against Hepatitis B virus formed,
LAB,Cholinesterase,CHE,>12000,Peningkatan Cholinesterase [XXXXX] U/L,"Konsultasi dengan dokter spesialis penyakit dalam dan dokter spesialis okupasi untuk pemeriksaan dan tata laksana lebih lanjut terkait peningkatan cholinesterase",Elevated cholinesterase [XXXXX] U/L,"Consult an internist and occupational medicine specialist for further evaluation and management of elevated cholinesterase"
LAB,Mikronutrien,Vit D,<20.0,Defisiensi vitamin D (Vitamin D 25-OH Total [XX.X] ng/mL),"Tingkatkan paparan sinar matahari pagi selama ±5–15 menit setiap hari, terutama pada area tangan dan kaki. Perbanyak konsumsi makanan kaya vitamin D (ikan laut, telur, susu, keju), serta pertimbangkan suplementasi vitamin D sesuai anjuran dokter",Vitamin D deficiency (Vitamin D 25-OH Total [XX.X] ng/mL),"Increase morning sun exposure for ±5–15 minutes daily, especially on arms and legs. Increase consumption of Vitamin D rich foods (sea fish, eggs, milk, cheese), and consider Vitamin D supplementation as advised by a doctor"
LAB,Mikronutrien,Vit D,>=20.0-29.9,Insufisiensi vitamin D (Vitamin D 25-OH Total [XX.X] ng/mL),"Tingkatkan paparan sinar matahari pagi selama ±5–15 menit setiap hari, terutama pada area tangan dan kaki. Perbanyak konsumsi makanan kaya vitamin D (ikan laut, telur, susu, keju), serta pertimbangkan suplementasi vitamin D sesuai anjuran dokter",Vitamin D insufficiency (Vitamin D 25-OH Total [XX.X] ng/mL),"Increase morning sun exposure for ±5–15 minutes daily, especially on arms and legs. Increase consumption of Vitamin D rich foods (sea fish, eggs, milk, cheese), and consider Vitamin D supplementation as advised by a doctor"
LAB,Urinalisa,Alb,[text_input],Albuminuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,Albuminuria [text_input] mg/dL,Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,keton,[text_input],Ketonuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,Ketonuria [text_input] mg/dL,Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,LE,[text_input],"Leukosituria [text_input]/uL, sedimen leukosit [text_input]/LPB",Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,"Leukocyturia [text_input]/uL, leukocyte sediment [text_input]/HPF",Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,Glukosuria,[text_input],Glukosuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,Glucosuria [text_input] mg/dL,Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,hema,[text_input],"Hematuria [text_input]/uL, sedimen eritrosit [text_input]/LPB",Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,"Hematuria [text_input]/uL, erythrocyte sediment [text_input]/HPF",Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,Kristal,,Kristaluria normal amorf urat (+)/LPB,Minum air putih minimal 2L/hari,Crystalluria normal amorphous urate (+)/HPF,Drink at least 2L of water/day
LAB,Urinalisa,urob,[text_input],Urobilinogenuria [text_input] mg/dL,Konsultasi dengan dokter spesialis urologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil urinalisa abnormal,Urobilinogenuria [text_input] mg/dL,Consult a urologist for further evaluation and management of abnormal urinalysis results
LAB,Urinalisa,Silinder kasar,[text_input],Silinder berbutir kasar [text_input]/LPK,Minum air putih minimal 2L/hari,Coarse granular cast [text_input]/LPF,Drink at least 2L of water/day
LAB,Urinalisa,Silinder halus,[text_input],Silinder berbutir halus [text_input]/LPK,Minum air putih minimal 2L/hari,Fine granular cast [text_input]/LPF,Drink at least 2L of water/day
LAB,Urinalisa,Epitel,[text_input],Epitel skuamosa [text_input]/LPK,Minum air putih minimal 2L/hari,Squamous epithelium [text_input]/LPF,Drink at least 2L of water/day
LAB,Urinalisa,Bakteri,,Bakteriuria (+)/LPB,Hindari kebiasaan menahan BAK dan jaga higienitas area genitalia,Bacteriuria (+)/HPF,Avoid delaying urination and maintain proper genital hygiene
LAB,Feses,FS,Parasit,Ditemukan parasit blastocystis hominis (+) pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal,Parasite blastocystis hominis (+) found in feces,Consult an internist for further evaluation and management of abnormal fecal analysis results
LAB,Feses,FS,Leuko,Ditemukan leukosit 0-1/LPB pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal,Leukocytes 0-1/HPF found in feces,Consult an internist for further evaluation and management of abnormal fecal analysis results
LAB,Feses,FS,Eri,Ditemukan eritrosit 0-1/LPB pada feses,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil analisa feses abnormal,Erythrocytes 0-1/HPF found in feces,Consult an internist for further evaluation and management of abnormal fecal analysis results
RONTGEN ,Thorax,Ro,Bronchitis,Rontgen Thorax: Bronchitis,Konsultasi dengan dokter spesialis paru untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal,Chest X-ray: Bronchitis,Consult a pulmonologist for further evaluation and management of abnormal chest X-ray findings
RONTGEN ,Thorax,Ro,Cardiomegali,Rontgen Thorax: Cardiomegali,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal,Chest X-ray: Cardiomegaly,Consult a cardiologist for further evaluation and management of abnormal chest X-ray findings
RONTGEN ,Thorax,Ro,Scoliosis,Rontgen Thorax: Dextroscoliosis thoracalis,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait temuan rontgen thorax abnormal,Chest X-ray: Dextroscoliosis thoracalis,Consult an orthopedic specialist for further evaluation and management of abnormal chest X-ray findings
AUDIOMETRI,Audiometri,Audio [AD; AS; ADS],[text_input],Audiometri [AD; AS; ADS]: [text_input],"Evaluasi faktor risiko dan etiologi terkait hasil audiometri [AD; AS; ADS] abnormal - Konsul dokter spesialis THT untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil audiometri [AD; AS; ADS] abnormal",[AD; AS; ADS] audiometry: [text_input],"Evaluate risk factors and etiology regarding abnormal audiometry results on [AD; AS; ADS] - Consult an ENT specialist for further evaluation and management of abnormal audiometry results on [AD; AS; ADS]"
SPIROMETRI,Spirometri,Spiro,Restriksi ringan,Spirometri: Restriksi ringan,Tingkatkan olahraga aerobik,Spirometry: Mild restriction,Increase aerobic exercise
SPIROMETRI,Spirometri,Spiro,Restriksi sedang,Spirometri: Restriksi sedang,"Tingkatkan olahraga aerobik - Konsul dokter spesialis paru untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil spirometri abnormal",Spirometry: Moderate restriction,"Increase aerobic exercise - Consult a pulmonologist for further evaluation and management of abnormal spirometry results"
SPIROMETRI,Spirometri,Spiro,Obstruksi ringan,Spirometri: Obstruksi ringan,Tingkatkan olahraga aerobik,Spirometry: Mild obstruction,Increase aerobic exercise
SPIROMETRI,Spirometri,Spiro,Obstruksi sedang,Spirometri: Obstruksi sedang,"Tingkatkan olahraga aerobik - Konsul dokter spesialis paru untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil spirometri abnormal",Spirometry: Moderate obstruction,"Increase aerobic exercise - Consult a pulmonologist for further evaluation and management of abnormal spirometry results"
EKG,EKG,EKG Taki,100-150,EKG: Sinus tachycardia HR [XXX] bpm normoaxis,Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal,ECG: Sinus tachycardia HR [XXX] bpm normoaxis,Consult a cardiologist if there are complaints regarding abnormal ECG results
EKG,EKG,EKG Bradi,30-59,EKG: Sinus bradycardia HR [XX] bpm normoaxis,Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal,ECG: Sinus bradycardia HR [XX] bpm normoaxis,Consult a cardiologist if there are complaints regarding abnormal ECG results
EKG,EKG,EKG RAD,50-99,"EKG: Sinus rhythm HR [XX] bpm, RAD",Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal,"ECG: Sinus rhythm HR [XX] bpm, RAD",Consult a cardiologist if there are complaints regarding abnormal ECG results
EKG,EKG,EKG LAD,50-99,"EKG: Sinus rhythm HR [XX] bpm, LAD",Konsultasi dengan dokter spesialis jantung jika ada keluhan terkait hasil EKG abnormal,"ECG: Sinus rhythm HR [XX] bpm, LAD",Consult a cardiologist if there are complaints regarding abnormal ECG results
TREADMILL,Treadmill,TMT,Iskemik,Treadmill test: Respon ischemic positive,Konsultasi dengan dokter spesialis jantung untuk pemeriksaan dan tatalaksana lebih lanjut terkait hasil Treadmill Test abnormal,Treadmill test: Positive ischemic response,Consult a cardiologist for further evaluation and management of abnormal Treadmill Test results
USG,USG Abdomen,USG Abd,[text_input],USG Whole Abdomen: [text_input],Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil USG Abdomen abnormal,USG Whole Abdomen: [text_input],Consult an internist for further evaluation and management of abnormal abdominal ultrasound results
USG,USG Mammae,USG MM,[text_input],USG Mammae: [text_input],Konsultasi dengan dokter spesialis bedah onkologi untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil USG Mammae abnormal,USG Mammae: [text_input],Consult a surgical oncologist for further evaluation and management of abnormal breast ultrasound results
SSBC,SSBC,SSBC,[text_input],SSBC: [text_input],Konsultasi dengan dokter spesialis obsgyn untuk pemeriksaan dan tata laksana lebih lanjut terkait hasil SSBC abnormal,SSBC: [text_input],Consult an Ob-Gyn specialist for further evaluation and management of abnormal Papsmear results
KONSUL,Konsul Gizi,Konsul Gizi,,,Konsultasi dengan dokter spesialis gizi klinik untuk tata laksana lebih lanjut terkait obesitas,,Consult a clinical nutrition specialist for further management of obesity
KONSUL,Konsul Dokter,Konsul sppd,[text_input],,Konsultasi dengan dokter spesialis penyakit dalam untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input],,Consult an internist for further evaluation and management of [text_input]
KONSUL,Konsul Dokter,Konsul spog,[text_input],,Konsultasi dengan dokter spesialis obsgyn untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input],,Consult an Ob-Gyn specialist for further evaluation and management of [text_input]
KONSUL,Konsul Dokter,Konsul sps,[text_input],,Konsultasi dengan dokter spesialis saraf untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input],,Consult a neurologist for further evaluation and management of [text_input]
KONSUL,Konsul Dokter,Konsul spb,[text_input],,Konsultasi dengan dokter spesialis bedah untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input],,Consult a surgeon for further evaluation and management of [text_input]
KONSUL,Konsul Dokter,Konsul spot,[text_input],,Konsultasi dengan dokter spesialis orthopedi untuk pemeriksaan dan tata laksana lebih lanjut terkait [text_input],,Consult an orthopedic specialist for further evaluation and management of [text_input]
ANAMNESIS,Keluhan,Keluhan,[text_input],Keluhan saat ini: [text_input],Konsultasi dengan dokter untuk pemeriksaan dan tata laksana lebih lanjut terkait keluhan saat ini,Current complaints: [text_input],Consult a doctor for further evaluation and management of current complaints
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

def replace_placeholders(text, row_input, matched_code_variant, lang='id'):
    """
    Mengganti placeholder dengan nilai, cerdas konteks (OD/OS, dll).
    Supports 'id' (Indonesian) and 'en' (English).
    """
    if not text: return ""
    processed_text = text
    
    # --- Language Specific Maps ---
    if lang == 'en':
        od_map = {"ODS": "both eyes", "OD": "the right eye", "OS": "the left eye"}
        
        # Contextual map for Audiometry vs others (e.g., Cerumen)
        if "audiometry" in text.lower():
             ad_map = {"ADS": "Both ears", "AD": "Right ear", "AS": "Left ear"}
        else:
             ad_map = {"ADS": "both ears", "AD": "the right ear", "AS": "the left ear"}
             
        side_map = {"DS": "both sides", "D": "the right", "S": "the left"} # Generic
        breast_map = {"DS": "both breasts", "D": "the right", "S": "the left"}
    else:
        od_map = {"ODS": "Mata kanan dan kiri", "OD": "Mata kanan", "OS": "Mata kiri"}
        ad_map = {"ADS": "Telinga kanan dan kiri", "AD": "Telinga kanan", "AS": "Telinga kiri"}
        side_map = {"DS": "kanan dan kiri", "D": "kanan", "S": "kiri"}
        breast_map = {"DS": "payudara kanan dan kiri", "D": "payudara kanan", "S": "payudara kiri"}

    # --- Logic 1: Mata & Telinga Contextual Replacement ---
    if "[OD; OS; ODS]" in processed_text:
        replacement = "Mata" if lang == 'id' else "Eyes"
        if matched_code_variant and "ODS" in matched_code_variant: replacement = od_map["ODS"]
        elif matched_code_variant and "OD" in matched_code_variant: replacement = od_map["OD"]
        elif matched_code_variant and "OS" in matched_code_variant: replacement = od_map["OS"]
        processed_text = processed_text.replace("[OD; OS; ODS]", replacement)

    if "[AD; AS; ADS]" in processed_text:
        replacement = "Telinga" if lang == 'id' else "Ears"
        if matched_code_variant and "ADS" in matched_code_variant: replacement = ad_map["ADS"]
        elif matched_code_variant and "AD" in matched_code_variant: replacement = ad_map["AD"]
        elif matched_code_variant and "AS" in matched_code_variant: replacement = ad_map["AS"]
        processed_text = processed_text.replace("[AD; AS; ADS]", replacement)
        
    if "[D; S; DS]" in processed_text:
        replacement = ""
        # Cek dari input juga karena kadang kode tidak memuat sisi (misal Ketok)
        tokens = row_input.upper().split()
        
        current_map = side_map
        
        # Context checks
        lower_text = processed_text.lower()
        if "payudara" in lower_text or "breast" in lower_text:
            current_map = breast_map
        elif lang == 'en' and "costovertebral angle tenderness" in lower_text:
            # Check for DS specifically for the phrasing change
            # Pattern: [D; S; DS] Costovertebral angle tenderness -> Costovertebral angle tenderness on both sides
            if "DS" in tokens or (matched_code_variant and "DS" in matched_code_variant):
                 processed_text = re.sub(r"\[D; S; DS\]\s*Costovertebral angle tenderness", "Costovertebral angle tenderness on both sides", processed_text, flags=re.IGNORECASE)
                 # Since placeholder is gone, we can skip the standard replacement logic below
            else:
                 # D or S logic
                 if processed_text.strip().startswith("[D; S; DS]"):
                     current_map = {"DS": "Bilateral", "D": "Right", "S": "Left"}
                 else:
                     current_map = {"DS": "bilateral", "D": "the right", "S": "the left"}

        # Standard Replacement (Only runs if placeholder still exists)
        if "[D; S; DS]" in processed_text:
            if "DS" in tokens or (matched_code_variant and "DS" in matched_code_variant): replacement = current_map["DS"]
            elif "D" in tokens or (matched_code_variant and "D" in matched_code_variant): replacement = current_map["D"]
            elif "S" in tokens or (matched_code_variant and "S" in matched_code_variant): replacement = current_map["S"]
            processed_text = processed_text.replace("[D; S; DS]", replacement)

    # --- Logic: Astigmatisme Check ---
    if "astig" in row_input.lower():
        if lang == 'en':
             processed_text = re.sub(r"\b(Myopia|Hypermetropia|Presbiopia)\b", r"\1 and astigmatism", processed_text, flags=re.IGNORECASE)
        else:
             processed_text = re.sub(r"\b(Miopia|Hipermetropia|Presbiopia)\b", r"\1 Astigmatisme", processed_text, flags=re.IGNORECASE)

    # --- Logic: Leukosituria & Hematuria (Complex Parsing) ---
    if ("Leukosituria" in text or "Hematuria" in text or "Leukocyturia" in text) and text.count("[text_input]") >= 2:
        clean_input = re.sub(r"^(leukosituria|hematuria|le|hema)\s*", "", row_input, flags=re.IGNORECASE).strip()
        match = re.search(r"^(.*?)(?:,?\s*sedimen\s*)(.*)$", clean_input, re.IGNORECASE)
        if match:
            val1 = match.group(1).strip()
            val2 = match.group(2).strip()
            processed_text = processed_text.replace("[text_input]", val1, 1)
            processed_text = processed_text.replace("[text_input]", val2, 1)
            return processed_text

    # --- Logic 2: Gigi (Parsing Khusus) ---
    if "Gigi: Gigi Hilang" in text or "Teeth: Missing teeth" in text:
        clean_input = re.sub(r"^Gigi\s*", "", row_input, flags=re.IGNORECASE).strip()
        segments = [s.strip() for s in clean_input.split(',')]
        dental_map = {}
        for seg in segments:
            parts = seg.split()
            if len(parts) >= 1:
                code = parts[0].upper()
                val = parts[1] if len(parts) > 1 else ""
                dental_map[code] = val
        
        # Template parts depends on language
        if lang == 'en':
             template_parts = [
                ('X', 'missing teeth ([X])'), ('R', 'root remnant ([R])'), ('A', 'abrasion ([A])'),
                ('C', 'caries ([C])'), ('E', 'calculus ([E])'), ('M', 'root canal treatment ([M])'),
                ('F', 'filling ([F])'), ('I', 'impaction ([I])'), ('P', 'denture ([P])'), ('FR', 'fractured tooth ([FR])')
            ]
             prefix = "Teeth: "
             default = "Teeth: No abnormalities"
        else:
             template_parts = [
                ('X', 'gigi hilang ([X])'), ('R', 'sisa akar ([R])'), ('A', 'abrasi ([A])'),
                ('C', 'karies ([C])'), ('E', 'karang gigi ([E])'), ('M', 'perawatan saluran akar ([M])'),
                ('F', 'tumpatan ([F])'), ('I', 'impaksi ([I])'), ('P', 'gigi palsu ([P])'), ('FR', 'gigi patah ([FR])')
            ]
             prefix = "Gigi: "
             default = "Gigi: Tidak ada kelainan"

        active_items = []
        for code, template_phrase in template_parts:
            if code in dental_map:
                active_items.append(template_phrase.replace(f"[{code}]", dental_map[code]))
        
        if active_items: processed_text = prefix + ", ".join(active_items)
        else: processed_text = default
        return processed_text

    # --- Logic 3: Numeric Placeholders ---
    search_text = row_input
    if matched_code_variant:
        pattern = re.compile(re.escape(matched_code_variant), re.IGNORECASE)
        search_text = pattern.sub("", row_input, count=1)
    
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", search_text)
    
    if "[XXX/XX]" in processed_text and "/" in row_input:
        match = re.search(r"(\d+/\d+)", row_input)
        if match: processed_text = processed_text.replace("[XXX/XX]", match.group(1))

    # Tensi dengan 3 digit (HT2)
    if "[XXX/XXX]" in processed_text and "/" in row_input:
        match = re.search(r"(\d+/\d+)", row_input)
        if match: processed_text = processed_text.replace("[XXX/XXX]", match.group(1))

    placeholders = re.findall(r"\[[A-Z\.]+\]", processed_text)
    numeric_placeholders = [p for p in placeholders if "OD" not in p and "AD" not in p and "DS" not in p and "text" not in p and "G" not in p]
    
    idx_num = 0
    for ph in numeric_placeholders:
        if ph in processed_text and idx_num < len(numbers):
            # Skip jika placeholder Tensi sudah dihandle
            if "/" in row_input and ("XXX/XX" in ph or "XXX/XXX" in ph): continue 
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
    keywords = ["obesitas", "overweight", "prehipertensi", "hipertensi", "prediabetes", "diabetes", 
                "obesity", "hyperglycemia", "hypertension"] # Added English keywords
    con_lower = conclusion_text.lower()
    return any(k in con_lower for k in keywords)

def handle_multi_visus(line, db, lang='id'):
    visus_matches = re.findall(r"\b(OD|OS|ODS)\s+(Miop|Hiper|Pres)\b", line, re.IGNORECASE)
    param_match = re.search(r"\b(TKM|DKM|Koreksi)\b", line, re.IGNORECASE)
    
    if len(visus_matches) >= 2 and param_match:
        param = param_match.group(0)
        parts_conclusions = []
        collected_advices = []
        suffix = ""
        
        for side, cond in visus_matches:
            synthetic_input = f"{side} {cond} {param}"
            if "astig" in line.lower():
                synthetic_input += " astig"
            
            match_row, matched_code, remainder = find_best_match(synthetic_input, db)
            
            if match_row is not None:
                # Select column based on lang
                col_conc = 'KESIMPULAN' if lang == 'id' else 'KESIMPULAN (English)'
                col_adv = 'SARAN KHUSUS' if lang == 'id' else 'SARAN KHUSUS (English)'

                raw_conc = str(match_row[col_conc])
                final_conc = replace_placeholders(raw_conc, synthetic_input, matched_code, lang)
                
                if "," in final_conc:
                    parts = final_conc.split(",", 1)
                    core = parts[0].strip()
                    suffix = parts[1].strip()
                    parts_conclusions.append(core)
                else:
                    parts_conclusions.append(final_conc)
                
                raw_adv = str(match_row[col_adv])
                final_adv = replace_placeholders(raw_adv, synthetic_input, matched_code, lang)
                if final_adv:
                    collected_advices.append(final_adv)
        
        if parts_conclusions:
            if suffix:
                merged_conclusion = ", ".join(parts_conclusions) + ", " + suffix
            else:
                merged_conclusion = ", ".join(parts_conclusions)
            return merged_conclusion, collected_advices
            
    return None, None

def process_patient_block(block, db):
    lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
    
    if len(lines) < 2: 
        return "Error: Data pasien tidak lengkap (Minimal: ID dan Nama)."
    
    p_id = lines[0]
    p_name = lines[1].upper()
    exam_lines = lines[2:]
    
    conclusions_id = []
    advices_id = []
    conclusions_en = []
    advices_en = []
    
    work_status_id = "Saran Kesehatan Kerja: Belum diinput"
    work_status_en = "Occupational Health Recommendation: Not input yet"
    needs_lifestyle = False
    
    for line in exam_lines:
        line_clean = line.strip().replace('\xa0', ' ') # Fix non-breaking space
        if line_clean.upper() == "FWN":
            work_status_id = "Saran Kesehatan Kerja: Sehat untuk bekerja dengan catatan"
            work_status_en = "Occupational Health Recommendation: Fit with Note"
            continue
        if line_clean.lower().startswith("temporary "):
            desc = re.sub(r"^temporary\s+", "", line_clean, flags=re.IGNORECASE)
            work_status_id = f"Saran Kesehatan Kerja: Tidak sehat untuk bekerja untuk sementara waktu ({desc})\n*Jika sudah melakukan konsultasi dengan dokter spesialis, mendapat tatalaksana dan hasil evaluasi membaik maka Sehat untuk bekerja dengan catatan"
            work_status_en = f"Occupational Health Recommendation: Temporary unfit ({desc})\n*If specialist consultation and management have been completed with improved results, the patient is fit to work with notes"
            continue
            
        # -- INDONESIA PROCESSING --
        multi_conc_id, multi_adv_id = handle_multi_visus(line, db, lang='id')
        if multi_conc_id:
            conclusions_id.append(multi_conc_id)
            if multi_adv_id: advices_id.extend(multi_adv_id)
        else:
            match_row, matched_code, remainder = find_best_match(line, db)
            if match_row is not None:
                raw_conc = str(match_row['KESIMPULAN'])
                final_conc = replace_placeholders(raw_conc, line, matched_code, lang='id')
                raw_adv = str(match_row['SARAN KHUSUS'])
                final_adv = replace_placeholders(raw_adv, line, matched_code, lang='id')
                
                if final_conc:
                    conclusions_id.append(final_conc)
                    if get_lifestyle_advice(final_conc): needs_lifestyle = True
                if final_adv:
                    advices_id.append(final_adv)
            else:
                conclusions_id.append(line) # Fallback if no match

        # -- ENGLISH PROCESSING --
        # Re-run logic for English to handle placeholders correctly
        multi_conc_en, multi_adv_en = handle_multi_visus(line, db, lang='en')
        if multi_conc_en:
            conclusions_en.append(multi_conc_en)
            if multi_adv_en: advices_en.extend(multi_adv_en)
        else:
            match_row, matched_code, remainder = find_best_match(line, db)
            if match_row is not None:
                raw_conc_en = str(match_row['KESIMPULAN (English)'])
                # Handle empty English fields if any
                if raw_conc_en == 'nan' or not raw_conc_en: raw_conc_en = ""
                
                final_conc_en = replace_placeholders(raw_conc_en, line, matched_code, lang='en')
                
                raw_adv_en = str(match_row['SARAN KHUSUS (English)'])
                if raw_adv_en == 'nan' or not raw_adv_en: raw_adv_en = ""
                
                final_adv_en = replace_placeholders(raw_adv_en, line, matched_code, lang='en')
                
                if final_conc_en: conclusions_en.append(final_conc_en)
                if final_adv_en: advices_en.append(final_adv_en)
            else:
                # If input has no match in DB, just print it as is (often text input)
                conclusions_en.append(line)

    # OUTPUT CONSTRUCTION
    output_str = f"{p_id}\n{p_name}\n\nKesimpulan:\n"
    for c in conclusions_id: output_str += f"{c}\n"
    
    output_str += "\nSaran:\n"
    final_advices_id = []
    if needs_lifestyle:
        final_advices_id.extend(["Jaga pola hidup sehat", "Olahraga secara teratur 3-5x/minggu, minimal 30 menit"])
    
    seen_adv = set(final_advices_id)
    for adv in advices_id:
        normalized_adv = adv.replace(" - ", "\n")
        subs = [s.strip().lstrip('-').strip() for s in normalized_adv.split('\n')]
        for sub in subs:
            if sub and sub not in seen_adv:
                final_advices_id.append(sub)
                seen_adv.add(sub)
    for fa in final_advices_id: output_str += f"{fa}\n"
    
    output_str += f"\n{work_status_id}\n"

    # ENGLISH SECTION
    output_str += "\nConclusion:\n"
    for c in conclusions_en: output_str += f"{c}\n"

    output_str += "\nRecommendation:\n"
    final_advices_en = []
    if needs_lifestyle:
        final_advices_en.extend(["Maintain a healthy lifestyle", "Exercise regularly 3–5 times per week, at least 30 minutes per session"])
    
    seen_adv_en = set(final_advices_en)
    for adv in advices_en:
        # Check for English delimiters if any, usually same structure
        normalized_adv = adv.replace(" - ", "\n")
        subs = [s.strip().lstrip('-').strip() for s in normalized_adv.split('\n')]
        for sub in subs:
            if sub and sub not in seen_adv_en:
                final_advices_en.append(sub)
                seen_adv_en.add(sub)
    
    for fa in final_advices_en: output_str += f"{fa}\n"
    
    output_str += f"\n{work_status_en}"

    return output_str

# ==========================================
# 3. MAIN APP
# ==========================================

st.title("🏥 Sarkes Generator (Resume MCU)")
st.markdown("Database sarkes dan format pengisian sarkes [klik disini](https://docs.google.com/spreadsheets/d/1LTL7hF06A-fFJBKqqouIfMUiIPzw1gc22-aIRHdUD3g/edit?usp=sharing).")
st.markdown("""

**Cara Pakai:**

1. Masukkan data pasien di kolom input (Untuk Multi-pasien gunakan pemisah `===PATIENT===`).
2. Klik tombol **Proses Sarkes**.
""", unsafe_allow_html=True)

# Load DB
try:
    db = load_db(csv_data)
    # Ensure columns are clean
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
        
        st.code("\n\n".join(results), language="markdown")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with 🤍 RianLab</p>", unsafe_allow_html=True)