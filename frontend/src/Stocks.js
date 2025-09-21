import React, { useEffect, useState } from "react";
import axios from "axios";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";

// Map API color names to CSS colors
const colorMap = {
  lightred: "#fca5a5",
  darkred: "#b91c1c",
  lightgreen: "#86efac",
  darkgreen: "#166534",
  gray: "#d1d5db",
};

const Stocks = ({ symbol, preloadedData }) => {
  const [tableData, setTableData] = useState(preloadedData || null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!symbol || preloadedData) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError("");

        const formData = new FormData();
        formData.append("symbol", symbol);

        const res = await axios.post("http://localhost:8000/history", formData);

        if (res.data.error) {
          setError(res.data.error);
          setTableData(null);
        } else {
          setTableData({
            data: res.data.data || [],
            result: res.data.result || {},
          });
        }
      } catch (err) {
        console.error(err);
        setError("Error fetching stock info");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, preloadedData]);

  const getValueColor = (key, value) => {
    if (
      typeof value === "string" &&
      (value === "Buy" || value === "Sell" || value === "Strong Buy")
    ) {
      return value.includes("Buy")
        ? "text-green-700 font-bold"
        : "text-red-700 font-bold";
    }
    return "text-gray-800";
  };

  if (loading) return <p className="text-blue-600">Loading stock data...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="w-full max-w-6xl mt-6 space-y-8">
      {tableData && (
        <>
          {/* Technical Indicators */}
          <Card
            sx={{ borderRadius: 3, boxShadow: "0 8px 20px rgba(0,0,0,0.12)" }}
          >
            <CardContent>
              <Typography
                variant="h6"
                className="font-bold text-gray-800 mb-4"
              >
                📊 Technical Indicators
              </Typography>
              <Grid container spacing={2}>
                {tableData.data.map((item) => {
                  const bgColor = colorMap[item.value[1]] || "#d1d5db"; // default gray
                  const label = item.value[2] || "";
                  return (
                    <Grid item xs={6} md={3} key={item.key}>
                      <Box
                        sx={{
                          p: 3,
                          borderRadius: 3,
                          backgroundColor: bgColor,
                          color: ["lightred", "darkred"].includes(item.value[1])
                            ? "white"
                            : "black",
                          transition: "all 0.3s ease",
                          "&:hover": {
                            boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                            transform: "translateY(-3px)",
                          },
                        }}
                      >
                        <Typography
                          variant="subtitle2"
                          className="uppercase tracking-wide"
                        >
                          {item.key}
                        </Typography>
                        <Typography variant="h6" className="font-bold mt-1">
                          {Array.isArray(item.value[0])
                            ? item.value[0].join(" / ")
                            : item.value[0]}
                        </Typography>
                        {label && (
                          <Typography variant="caption" className="mt-1 block">
                            {label}
                          </Typography>
                        )}
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>

          {/* Fundamentals */}
          <Card
            sx={{ borderRadius: 3, boxShadow: "0 8px 20px rgba(0,0,0,0.12)" }}
          >
            <CardContent>
              <Typography
                variant="h6"
                className="font-bold text-gray-800 mb-4"
              >
                🏦 Fundamentals
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(tableData.result).map(([key, value]) => (
                  <Grid item xs={6} md={3} key={key}>
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 3,
                        backgroundColor:
                          typeof value === "number"
                            ? value >= 0
                              ? "#86efac" // light green
                              : "#fca5a5" // light red
                            : "#d1d5db", // gray for strings
                        color:
                          typeof value === "number"
                            ? value >= 0
                              ? "black"
                              : "white"
                            : "black",
                        transition: "all 0.3s ease",
                        "&:hover": {
                          boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                          transform: "translateY(-3px)",
                        },
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        className="uppercase tracking-wide"
                      >
                        {key}
                      </Typography>
                      <Typography
                        variant="h6"
                        className={`${getValueColor(key, value)} mt-1`}
                      >
                        {value}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default Stocks;
