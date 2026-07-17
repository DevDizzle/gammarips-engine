URL="https://blog-generator-406581297632.us-central1.run.app/generate"
for slug in systems-problem-not-pick-problem whatsapp-group-tag-the-agent whats-pushed-to-my-phone-at-9am; do
  echo "===== REGEN $slug ====="
  curl -s --max-time 880 -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d "{\"slug\": \"$slug\"}" \
    -w "\nHTTP_STATUS=%{http_code}\n"
  echo ""
done
echo "ALL_DONE"
