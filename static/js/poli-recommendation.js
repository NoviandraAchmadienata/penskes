// Poli to specialization mapping
const POLI_TO_SPEC = {
    'Poli Anak': 'anak',
    'Poli Bedah': 'bedah',
    'Poli Gigi': 'gigi',
    'Poli Umum': 'penyakit-dalam'
};

async function getPoliRecommendation() {
    const complaint = document.getElementById('chiefComplaint').value.trim();
    const age = document.getElementById('patientAge').value;
    const duration = document.getElementById('complaintDuration').value;

    if (!complaint || !age || !duration) {
        alert('Mohon isi semua data: Keluhan Utama, Usia, dan Durasi Keluhan');
        return;
    }

    const poliInput = document.getElementById('recommendedPoli');
    poliInput.value = 'Sedang memproses...';

    try {
        const response = await fetch('/api/recommend-poli', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                complaint: complaint,
                age: parseInt(age),
                duration: parseInt(duration)
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            poliInput.value = 'Gagal mendapatkan rekomendasi';
            console.error('Error:', data.error);
            return;
        }

        const recommendedPoli = data.recommended_poli;
        poliInput.value = recommendedPoli;

        // Auto-select specialization based on poli
        const specValue = POLI_TO_SPEC[recommendedPoli];
        if (specValue) {
            document.getElementById('specialization').value = specValue;
        }
    } catch (error) {
        poliInput.value = 'Gagal menghubungi server';
        console.error('Fetch error:', error);
    }
}

// Allow Enter key to trigger recommendation
document.addEventListener('DOMContentLoaded', function() {
    ['chiefComplaint', 'patientAge', 'complaintDuration'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') getPoliRecommendation();
            });
        }
    });
});
