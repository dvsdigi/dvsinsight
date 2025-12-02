document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('fetchBtn');
    const enrollBtn = document.getElementById('enrollBtn');
    const studentIdInput = document.getElementById('studentIdInput');
    const previewSection = document.getElementById('previewSection');
    const messageDiv = document.getElementById('message');

    // State to hold current student data
    let currentStudent = null;

    fetchBtn.addEventListener('click', async () => {
        const studentId = studentIdInput.value.trim();
        if (!studentId) {
            showMessage('Please enter a Student ID', 'error');
            return;
        }

        try {
            fetchBtn.disabled = true;
            fetchBtn.textContent = 'Fetching...';
            showMessage('', 'hidden');
            previewSection.classList.add('hidden');

            const response = await fetch(`/enroll/fetch/${studentId}`);
            if (!response.ok) {
                throw new Error('Student not found or API error');
            }

            const data = await response.json();
            currentStudent = data;

            // Update UI
            document.getElementById('previewId').textContent = data.student_id;
            document.getElementById('previewName').textContent = data.student_name;
            document.getElementById('previewSchoolId').textContent = data.school_id;
            document.getElementById('previewImage').src = data.photo_url;

            previewSection.classList.remove('hidden');
        } catch (error) {
            showMessage(error.message, 'error');
            currentStudent = null;
        } finally {
            fetchBtn.disabled = false;
            fetchBtn.textContent = 'Fetch Details';
        }
    });

    enrollBtn.addEventListener('click', async () => {
        if (!currentStudent) return;

        try {
            enrollBtn.disabled = true;
            enrollBtn.textContent = 'Enrolling...';

            const formData = new FormData();
            formData.append('student_id', currentStudent.student_id);
            formData.append('student_name', currentStudent.student_name);
            formData.append('photo_url', currentStudent.photo_url);
            formData.append('school_id', currentStudent.school_id);

            const response = await fetch('/enroll/save', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Enrollment failed');
            }

            showMessage(result.message, 'success');
            // Optional: Clear form
            // studentIdInput.value = '';
            // previewSection.classList.add('hidden');
            // currentStudent = null;

        } catch (error) {
            showMessage(error.message, 'error');
        } finally {
            enrollBtn.disabled = false;
            enrollBtn.textContent = 'Enroll Student';
        }
    });

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = type === 'hidden' ? 'hidden' : type;
        if (type !== 'hidden') {
            messageDiv.classList.remove('hidden');
        }
    }
});
