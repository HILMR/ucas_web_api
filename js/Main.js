function main(password)
{
	setMaxDigits(130);
	var key = new RSAKeyPair("10001","","9c2899b8ceddf9beafad2db8e431884a79fd9b9c881e459c0e1963984779d6612222cee814593cc458845bbba42b2d3474c10b9d31ed84f256c6e3a1c795e68e18585b84650076f122e763289a4bcb0de08762c3ceb591ec44d764a69817318fbce09d6ecb0364111f6f38e90dc44ca89745395a17483a778f1cc8dc990d87c3");
	password = encryptedString(key, password);
	return password;
}