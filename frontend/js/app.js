
document.getElementById('baconForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const actorName = document.getElementById('actorName').value.trim();
  const resultDiv = document.getElementById('result');

  if (!actorName) {
    resultDiv.textContent = 'Please enter an actor name.';
    return;
  }

  resultDiv.textContent = 'Caclulating...';

  try {
    const response = await fetch(`/api/bacon_distance?actor_name=${encodeURIComponent(actorName)}`);



    if (!response.ok) {

      // If the response is not ok, handle the error
      const errorData = await response.json();
      const errorMessage = errorData.detail?.message || "An unknown error occurred.";
      const errorDescription = errorData.detail?.description || "No further details available.";

      resultDiv.textContent = `Error: ${errorMessage} ${errorDescription}`;
    } else {

      const data = await response.json();
      resultDiv.textContent = `Bacon distance for "${actorName}": ${data.bacon_distance}`;
    }
  } catch (error) {
    resultDiv.textContent = `Error: ${error.message}`;
  }
});
