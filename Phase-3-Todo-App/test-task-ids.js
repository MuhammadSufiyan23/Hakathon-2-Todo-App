// Test Script - Run in Browser Console
// Copy and paste this entire script into your browser console (F12)

async function testTaskIDSystem() {
  console.log('='.repeat(60));
  console.log('🧪 TASK ID SYSTEM TEST');
  console.log('='.repeat(60));

  // Step 1: Get auth token
  console.log('\n📋 Step 1: Getting auth token...');
  const auth = localStorage.getItem('auth');
  if (!auth) {
    console.error('❌ FAIL: No auth token found. Please login first.');
    return;
  }

  const authData = JSON.parse(auth);
  const token = authData.token;
  console.log('✅ Auth token found');

  // Step 2: Create a test task
  console.log('\n📋 Step 2: Creating test task...');
  const testTitle = 'Test Task ' + Date.now();

  try {
    const response = await fetch('http://localhost:8000/api/tasks', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: testTitle,
        description: 'Testing unique IDs',
        priority: 'medium'
      })
    });

    if (!response.ok) {
      console.error('❌ FAIL: API returned error:', response.status);
      const error = await response.json();
      console.error('Error details:', error);
      return;
    }

    const data = await response.json();
    console.log('✅ Task created successfully');
    console.log('\n📊 Response Data:');
    console.log('  UUID:', data.id);
    console.log('  displayId:', data.displayId);
    console.log('  Title:', data.title);

    // Step 3: Validate IDs
    console.log('\n📋 Step 3: Validating IDs...');

    let passed = 0;
    let failed = 0;

    // Test 1: UUID exists
    if (data.id) {
      console.log('✅ PASS: UUID exists');
      passed++;
    } else {
      console.error('❌ FAIL: UUID missing');
      failed++;
    }

    // Test 2: UUID is valid format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (uuidRegex.test(data.id)) {
      console.log('✅ PASS: UUID has valid format');
      passed++;
    } else {
      console.error('❌ FAIL: UUID has invalid format');
      failed++;
    }

    // Test 3: displayId exists
    if (data.displayId !== undefined && data.displayId !== null) {
      console.log('✅ PASS: displayId exists');
      passed++;
    } else {
      console.error('❌ FAIL: displayId missing');
      failed++;
    }

    // Test 4: displayId is a number
    if (typeof data.displayId === 'number') {
      console.log('✅ PASS: displayId is a number');
      passed++;
    } else {
      console.error('❌ FAIL: displayId is not a number');
      failed++;
    }

    // Test 5: displayId is positive
    if (data.displayId > 0) {
      console.log('✅ PASS: displayId is positive');
      passed++;
    } else {
      console.error('❌ FAIL: displayId is not positive');
      failed++;
    }

    // Step 4: Test uniqueness
    console.log('\n📋 Step 4: Testing uniqueness...');
    console.log('Creating second task...');

    const response2 = await fetch('http://localhost:8000/api/tasks', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: 'Test Task 2 ' + Date.now(),
        description: 'Testing uniqueness'
      })
    });

    const data2 = await response2.json();
    console.log('Second task created');
    console.log('  UUID:', data2.id);
    console.log('  displayId:', data2.displayId);

    // Test 6: UUIDs are different
    if (data.id !== data2.id) {
      console.log('✅ PASS: UUIDs are unique');
      passed++;
    } else {
      console.error('❌ FAIL: UUIDs are the same!');
      failed++;
    }

    // Test 7: displayIds are different
    if (data.displayId !== data2.displayId) {
      console.log('✅ PASS: displayIds are different');
      passed++;
    } else {
      console.error('❌ FAIL: displayIds are the same!');
      failed++;
    }

    // Final Results
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST RESULTS');
    console.log('='.repeat(60));
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📈 Success Rate: ${Math.round((passed / (passed + failed)) * 100)}%`);

    if (failed === 0) {
      console.log('\n🎉 ALL TESTS PASSED! Task ID system is working correctly.');
    } else {
      console.log('\n⚠️ SOME TESTS FAILED. Please check the errors above.');
    }

    console.log('\n💡 Next Steps:');
    console.log('1. Check if task cards show displayId badges in UI');
    console.log('2. Test chatbot: "Add a task to buy milk"');
    console.log('3. Verify chatbot mentions task number in response');

  } catch (error) {
    console.error('❌ ERROR:', error);
    console.error('\n💡 Troubleshooting:');
    console.error('1. Make sure backend is running: http://localhost:8000');
    console.error('2. Check .env.local: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api');
    console.error('3. Restart both backend and frontend');
  }
}

// Run the test
console.log('🚀 Starting Task ID System Test...\n');
testTaskIDSystem();
