var show_negative = function(neg) {
	if (neg) {
		$("#negative").text("negatiivinen");
	} else {
		$("#negative").text("");
	}
};

var populate_question = function(data) {
	$("#infinitive").text(data.infinitive);
	$("#person").text(data.person);
	$("#tense").text(data.tense);
	show_negative(data.negative);
	var check_answer = function() {
		var user_answer = $("#answer").val().toLowerCase().trim();
		if (user_answer == data.answer) {
			$("#judgment").empty().text("✔ Kyllä!").removeClass("alert-danger").addClass("alert-success");
			window.scores.rights[data.index]++;
		} else {
			var answerdiv = $("<div>");
			answerdiv.append($("<span>").text("✘ "));
			var dmp = new diff_match_patch();
			var diff = dmp.diff_main(user_answer, data.answer);
			dmp.diff_cleanupSemantic(diff);
			// Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
			for (let k in diff) {
				let d = diff[k];
				let el = null;
				if (d[0] == -1) {
					el = $("<del>");
				} else if (d[0] == 1) {
					el = $("<ins>");
				} else {
					el = $("<span>");
				}
				answerdiv.append(el.text(d[1]));
			}
			answerdiv.append($("<br>"));
			answerdiv.append($("<span>").text(data.answer));
			console.log(answerdiv);
			$("#judgment").empty().append(answerdiv).removeClass("alert-success").addClass("alert-danger");
			window.scores.wrongs[data.index]++;
		}
		localStorage.setItem("scores", JSON.stringify(window.scores));
		display_scores();
		$("#check").removeClass("btn-primary").addClass("btn-secondary").removeAttr('type');
		$("#new").removeClass("btn-secondary").addClass("btn-primary").attr('type', 'submit');
		$("form").off('submit').on('submit', function(e) {
			e.preventDefault();
			get_question();
		});
	};
	$("#check").removeClass("btn-secondary").addClass("btn-primary").attr('type', 'submit');
	$("#new").removeClass("btn-primary").addClass("btn-secondary").removeAttr('type');
	$("form").off('submit').on('submit', function(e) {
		e.preventDefault();
		check_answer();
	});
};

var get_question = function() {
	$.getJSON("/generate_example/?"+$("form").serialize(), populate_question);
	$("#answer").val('');
	$("#judgment").text('').removeClass("alert-danger alert-success");
};

var get_scores = function() {
	var total_wrongs = 0;
	var total_rights = 0;
	for (let k in window.scores.rights) {
		total_rights += window.scores.rights[k];
	}
	for (let k in scores.wrongs) {
		total_wrongs += window.scores.wrongs[k];
	}
	var total = total_rights + total_wrongs;
	return {
		"rights": total_rights,
		"wrongs": total_wrongs,
		"total": total_rights+total_wrongs,
		"percent": 100.0 * total_rights / total || 0
	};
};

var display_scores = function() {
	var summed_scores = get_scores();
	$("#rights").text(summed_scores.rights);
	$("#total").text(summed_scores.total);
	$("#percent").text(Math.round(100*summed_scores.percent)/100);
}

var setup_scores = function() {
	var s = localStorage.getItem("scores");
	if (s) {
		window.scores = JSON.parse(s);
	} else {
		// array key is {verbtype|tense|negation|person}
		// verbtype 1 to 6
		// tense 1 = present, 2 = imperfect, 3 = perfect, 4 = pluperfect
		// negation 1 = positive, 2 = negative
		// person 1 = SG1, ... 6 = PL3
		window.scores = {"rights": {}, "wrongs": {}};
		for (var verbtype=1; verbtype<7; verbtype++) {
			for (var tense=1; tense<5; tense++) {
				for (var negative=1; negative<3; negative++) {
					for (var person=1; person<7; person++) {
						var index =	
							verbtype.toString() +
							tense.toString() +
							negative.toString() +
							person.toString();
						window.scores.rights[index] = 0;
						window.scores.wrongs[index] = 0;
					}
				}
			}
		}
		localStorage.setItem("scores", JSON.stringify(window.scores));
	}
};
var clear_scores = function() {
	window.scores = null;
	localStorage.removeItem("scores");
	setup_scores();
	display_scores();
};

$(document).ready( function() {
	setup_scores();
	display_scores();
	get_question();
});
