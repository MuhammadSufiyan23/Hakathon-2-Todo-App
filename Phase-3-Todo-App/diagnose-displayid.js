// DIAGNOSTIC SCRIPT - Run in Browser Console
// This will tell us exactly what's wrong

async function diagnoseDisplayIdIssue() {
  console.clear();
  console.log('='.repeat(70));
  console.log('🔍 DISPLAY ID DIAGNOSTIC');
  console.log('='.repeat(70));

  // Step 1: Check auth
  console.log('\n📋 Step 1: Checking authentication...');
  const auth = localStorage.getItem('auth');
  if (!auth) {
    console.error('❌ FAIL: No auth token. Please login first.');
    return;
  }
  const token = JSON.parse(auth).token;
  console.log('✅ Auth token found');

  // Step 2: Check backend directly
  console.log('\n📋 Step 2: Checking backend response...');
  try {
    const backendResponse = await fetch('http://localhost:8000/api/tasks', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!backendResponse.ok) {
      console.error('❌ Backend error:', backendResponse.status);
      return;
    }

    const backendData = await backendResponse.json();
    console.log('✅ Backend responded');
    console.log('📊 Backend raw response:', backendData);

    if (Array.isArray(backendData)) {
      console.log('✅ Response is an array');
      console.log('📊 Number of tasks:', backendData.length);

      if (backendData.length > 0) {
        const firstTask = backendData[0];
        console.log('\n📊 First task analysis:');
        console.log('  - id:', firstTask.id);
        console.log('  - displayId:', firstTask.displayId);
        console.log('  - display_id:', firstTask.display_id);
        console.log('  - title:', firstTask.title);

        if (firstTask.displayId) {
          console.log('✅ displayId EXISTS in backend response');
        } else if (firstTask.display_id) {
          console.error('❌ PROBLEM: Backend returns display_id (snake_case) not displayId (camelCase)');
        } else {
          console.error('❌ PROBLEM: Backend NOT returning displayId at all');
        }
      }
    } else {
      console.error('❌ PROBLEM: Backend not returning array');
    }

  } catch (error) {
    console.error('❌ Backend request failed:', error);
    return;
  }

  // Step 3: Check frontend transform
  console.log('\n📋 Step 3: Checking frontend transform...');
  console.log('Check console for [API Transform] logs when page loads');

  // Step 4: Check React state
  console.log('\n📋 Step 4: Checking React component state...');
  console.log('Open React DevTools and check:');
  console.log('  1. Find AllTasksPage component');
  console.log('  2. Check "tasks" state');
  console.log('  3. Verify each task has displayId property');

  // Step 5: Check TaskCard rendering
  console.log('\n📋 Step 5: Checking TaskCard component...');
  console.log('In React DevTools:');
  console.log('  1. Find TaskCard component');
  console.log('  2. Check props.task.displayId');
  console.log('  3. Verify badge is rendering');

  console.log('\n' + '='.repeat(70));
  console.log('📊 DIAGNOSTIC COMPLETE');
  console.log('='.repeat(70));
  console.log('\n💡 Next: Check the output above to find the exact problem');
}

// Run diagnostic
diagnoseDisplayIdIssue();
