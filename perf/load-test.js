// Temel oluşturma akışı için yük testi senaryosu.
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<800"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const payload = JSON.stringify({
    text: `https://example.com/k6/${__VU}/${__ITER}`,
    label: `k6-${__VU}-${__ITER}`,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const response = http.post(`${baseUrl}/api/v1/qrcodes`, payload, params);
  check(response, {
    "create status is 201": (res) => res.status === 201,
  });

  sleep(1);
}
