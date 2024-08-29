#/bin/bash
cd ../

echo "================Running AutoTest================"

echo "================Running AutoTest.character================"
python -m AutoTest.character

echo "================Running AutoTest.style================"
python -m AutoTest.style

echo "================Running AutoTest.emotion================"
python -m AutoTest.emotion

echo "================Running AutoTest.relationship================"
python -m AutoTest.relationship

echo "================Running AutoTest.personality================"
python -m AutoTest.personality

echo "================Running AutoTest.human_likeness================"
python -m AutoTest.human_likeness

echo "================Running AutoTest.rolechoice================"
python -m AutoTest.rolechoice

echo "================Running AutoTest.coherence================"
python -m AutoTest.coherence