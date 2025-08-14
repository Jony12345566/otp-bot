<?php
// ===== CONFIGURE =====
$botToken = "8432191653:AAHUuOR485CXKkxg3TNL3ZIxRruxdIXK6Cs";  // Telegram Bot Token
$chatId   = "7128914520";             // Telegram Chat ID
$url      = "http://94.23.120.156/ints/agent/res/data_smscdr.php?fdate1=2025-08-14%2000:00:00&fdate2=2025-08-14%2023:59:59&frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgclient=&fgnumber=&fgcli=&fg=0&sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=25&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&mDataProp_7=7&sSearch_7=&bRegex_7=false&bSearchable_7=true&bSortable_7=true&mDataProp_8=8&sSearch_8=&bRegex_8=false&bSearchable_8=true&bSortable_8=false&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_=1755166404081";             // OTP API URL
$cookie   = "PHPSESSID=me7a511lshd41kjt0jm02m2ji9";// আপনার PHPSESSID

$sentOtps = []; // Already sent OTPs

while (true) {
    // Step 1: Fetch data
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ["Cookie: $cookie"]);
    $response = curl_exec($ch);
    curl_close($ch);

    // Step 2: Decode JSON
    $data = json_decode($response, true);

    // Step 3: Extract OTPs (4-8 digits)
    if (!empty($data['aaData'])) {
        foreach ($data['aaData'] as $row) {
            $text = implode(" ", $row);
            if (preg_match_all('/\b\d{4,8}\b/', $text, $matches)) {
                foreach ($matches[0] as $otp) {
                    if (!in_array($otp, $sentOtps)) {
                        $sentOtps[] = $otp;
                        // Step 4: Send to Telegram
                        file_get_contents(
                            "https://api.telegram.org/bot$botToken/sendMessage?chat_id=$chatId&text=" . urlencode("🔐 New OTP: $otp")
                        );
                    }
                }
            }
        }
    }

    sleep(10); // প্রতি 10 সেকেন্ডে চেক
}
?>
