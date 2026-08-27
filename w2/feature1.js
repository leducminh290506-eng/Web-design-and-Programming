
let thpt_score = {name : "mlecute", Math : 10, Literature : 9.75 , English : 9.75};
// Calculate total score of thpt_score
let sum = thpt_score.Math + thpt_score.Literature + thpt_score.English;
console.log("sum of thpt_score: " +  sum);
// Check all subject that have score above 8
for (let subject in thpt_score) {
    if (subject !== "name " && thpt_score[subject] > 8)
        console.log(subject + " has score more than 8");
}
// Calculate the highest score of thpt_score
let current_score = 0;
for (let subject in thpt_score) {
    if (subject !== "name" && thpt_score[subject] > current_score) {
        current_score = thpt_score[subject];
        console.log("Highest subject score is: " + subject + " with " + current_score);
    }
}