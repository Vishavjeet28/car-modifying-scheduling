# Manual Booking Test Guide

## 🎯 **Step-by-Step Booking Test**

Follow these steps to test the new slot interface and identify any issues:

### **Step 1: Access the Page**
1. Open your browser
2. Go to: `http://127.0.0.1:8000/services/7/book/`
3. You should be redirected to login page

### **Step 2: Login**
Use one of these existing customer accounts:
- **Username:** `test` 
- **Username:** `newest`
- **Username:** `webtest`

Try common passwords like: `password`, `123456`, `admin123`, or the username itself.

**Or create a new account:**
1. Go to: `http://127.0.0.1:8000/accounts/register/`
2. Create a new customer account
3. Login with your new credentials

### **Step 3: Test the New Slot Interface**

Once logged in and on the booking page:

1. **Open Browser Console** (F12 → Console tab)
2. **Select a Date** - Choose tomorrow's date or any future date
3. **Watch Console Logs** - You should see:
   ```
   🎯 New Slot Interface JavaScript Loaded
   📋 Element Check: (all should be true)
   Fetching slots for date: 2025-10-16
   API response data: {...}
   ```

4. **Check Slot Cards** - Time slots should appear as clickable cards
5. **Click a Time Slot** - You should see:
   ```
   Slot card clicked: 09:00
   Slot clicked: 09:00 9:00 AM
   New selected slot: {time: "09:00", display: "9:00 AM"}
   ```

6. **Check Button State** - The submit button should:
   - Change from "Select Time Slot" to "Confirm Booking (9:00 AM)"
   - Become enabled (not grayed out)

### **Step 4: Complete the Form**

Fill in vehicle information:
- **Vehicle Make:** Toyota
- **Vehicle Model:** Camry  
- **Vehicle Year:** 2020
- **License Plate:** TEST-123

### **Step 5: Submit the Form**

1. Click "Confirm Booking"
2. Watch console for:
   ```
   Form submission attempted
   Selected slot: {time: "09:00", display: "9:00 AM"}
   Hidden input value: 09:00
   ```

## 🔍 **Common Issues & Solutions**

### **Issue 1: No Slot Cards Appear**
**Console Error:** `API response data: undefined`
**Solution:** Check if you're logged in and the API endpoint works

### **Issue 2: Slot Cards Don't Respond to Clicks**
**Console Error:** No logs when clicking slots
**Solution:** Cards might not be created properly - check for JavaScript errors

### **Issue 3: Submit Button Stays Disabled**
**Console Shows:** `Submit button disabled`
**Solution:** 
- Make sure you clicked a slot card
- Check if `selectedSlot` variable is set
- Verify hidden input has a value

### **Issue 4: Form Submission Fails**
**Console Shows:** `Form submission prevented - no slot selected`
**Solution:**
- Ensure slot selection worked
- Check hidden input value: `document.getElementById('id_slot_time').value`

## 🛠️ **Quick Debugging Commands**

Open browser console and try these:

```javascript
// Check if elements exist
console.log('Form:', document.getElementById('booking-form'));
console.log('Date input:', document.getElementById('id_slot_date'));
console.log('Time input:', document.getElementById('id_slot_time'));
console.log('Submit button:', document.getElementById('book-btn'));

// Check slot selection
console.log('Selected slot:', selectedSlot);
console.log('Hidden time value:', document.getElementById('id_slot_time').value);

// Test API directly
fetch('/appointments/api/available-slots/?date=2025-10-16')
  .then(response => response.json())
  .then(data => console.log('API data:', data));
```

## 📋 **Expected Behavior**

### **Working Flow:**
1. ✅ Page loads with debugging messages
2. ✅ Date selection triggers slot loading
3. ✅ Slot cards appear and are clickable
4. ✅ Slot selection updates button text
5. ✅ Form submission works without errors

### **Visual Indicators:**
- **Available slots:** White cards with blue hover effect
- **Selected slot:** Blue gradient background with white text
- **Submit button:** Shows selected time, e.g., "Confirm Booking (9:00 AM)"
- **Booking summary:** Appears below form with selected details

## 🚨 **If Nothing Works**

1. **Clear browser cache:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Check server logs:** Look at terminal running Django server
3. **Verify user permissions:** Make sure you're logged in as customer
4. **Test API endpoint directly:** Visit `/appointments/api/available-slots/?date=2025-10-16`

## 📞 **Report Issues**

If you find issues, please share:
1. **Browser console logs** (copy the text)
2. **What step failed** (date selection, slot clicking, form submission)
3. **Error messages** (if any)
4. **Browser and version** you're using

---

**Remember:** All debugging information will appear in the browser console, so keep it open while testing!