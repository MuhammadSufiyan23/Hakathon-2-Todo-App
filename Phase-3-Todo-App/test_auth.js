// Simple test to check if the frontend can communicate with the backend
const testAuthFlow = async () => {
  try {
    console.log('Testing signup...');

    const signupResponse = await fetch('http://localhost:8000/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'testuser3@example.com',
        password: 'password123',
        name: 'Test User 3'
      })
    });

    const signupData = await signupResponse.json();
    console.log('Signup response:', signupData);

    if (signupResponse.ok) {
      console.log('Signup successful!');

      console.log('Testing login...');
      const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'testuser3@example.com',
          password: 'password123'
        })
      });

      const loginData = await loginResponse.json();
      console.log('Login response:', loginData);

      if (loginResponse.ok) {
        console.log('Login successful!');

        // Test getting user profile with the token
        const profileResponse = await fetch('http://localhost:8000/api/auth/profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${loginData.token}`
          }
        });

        const profileData = await profileResponse.json();
        console.log('Profile response:', profileData);

        if (profileResponse.ok) {
          console.log('Profile retrieval successful!');
        } else {
          console.log('Profile retrieval failed:', profileData);
        }
      } else {
        console.log('Login failed:', loginData);
      }
    } else {
      console.log('Signup failed:', signupData);
    }
  } catch (error) {
    console.error('Error during auth flow test:', error);
  }
};

testAuthFlow();