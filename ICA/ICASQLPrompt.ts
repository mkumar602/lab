//generate SQL code for : "what is the Total fd investment for silver customers with more than 1000 loyalty points and who live in New York"
// This code is generated using model Starcoder 
SELECT SUM(FD.Amount)
FROM FinancialData AS FD
INNER JOIN Customer AS C
ON C.CustomerID = FD.CustomerID
INNER JOIN LyaltyPoints AS LP
ON LP.CustomerID = C.CustomerID
WHERE C.LoyaltyPoints > 1000
AND C.City = "New York"
AND FD.Security